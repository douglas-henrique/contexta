import logging
import time
from pathlib import Path
from typing import Optional

from ingest.chunking.semantic import semantic_chunk
from ingest.embeddings.openai import embed_texts
from ingest.loaders.pdf import load_pdf
from ingest.vectorstore.qdrant import store_embeddings

logger = logging.getLogger(__name__)


def _detect_file_type(file_path: str) -> str:
    """Detect file type from extension."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return "pdf"
    elif extension in [".txt", ".text"]:
        return "txt"
    elif extension == ".docx":
        return "docx"
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def _load_txt(file_path: str) -> str:
    """Load text file content."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Try different encodings
    encodings = ["utf-8", "latin-1", "cp1252"]
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Could not decode file: {file_path}")


def _load_document(file_path: str, file_type: str) -> str:
    """Load document content based on file type."""
    if file_type == "pdf":
        return load_pdf(file_path)
    elif file_type == "txt":
        return _load_txt(file_path)
    elif file_type == "docx":
        raise NotImplementedError("DOCX loading not yet implemented")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def ingest_document(
    document_id: int,
    file_path: str,
    metadata: dict,
    tenant_id: int,
    callback_url: Optional[str] = None,
):
    """
    Ingest a document into the vector store.

    Args:
        document_id: ID of the document
        file_path: Path to the document file
        metadata: Additional metadata
        tenant_id: Tenant identifier for multi-tenant isolation
        callback_url: Optional URL to call when ingestion completes
    """
    try:
        logger.info(f"Starting ingestion for document {document_id} (tenant {tenant_id})")

        # 1. Detect and load document
        file_type = _detect_file_type(file_path)
        logger.debug(f"Detected file type: {file_type}")

        text = _load_document(file_path, file_type)
        if not text or not text.strip():
            raise ValueError(f"Document {document_id} is empty")
        logger.debug(f"Loaded {len(text)} characters from document")

        # 2. Chunk content
        chunks = semantic_chunk(text)
        logger.info(f"Created {len(chunks)} chunks from document {document_id}")

        if not chunks:
            raise ValueError(f"No chunks created from document {document_id}")

        # 3. Generate embeddings
        logger.debug(f"Generating embeddings for {len(chunks)} chunks")
        embeddings = embed_texts(chunks)
        logger.debug(f"Generated {len(embeddings)} embeddings")

        if len(chunks) != len(embeddings):
            raise ValueError("Mismatch between chunks and embeddings count")

        # 4. Store in vector store
        logger.debug(f"Storing {len(chunks)} chunks in vector store")
        store_embeddings(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
            tenant_id=tenant_id,
        )

        logger.info(f"Document {document_id} ingested successfully (tenant {tenant_id})")

        # 5. Callback if provided
        if callback_url:
            _send_callback_with_retry(
                callback_url,
                {
                    "document_id": document_id,
                    "status": "completed",
                    "chunks_created": len(chunks),
                },
                document_id,
            )

    except FileNotFoundError as e:
        logger.error(f"File not found for document {document_id}: {e}")
        _send_failed_callback(callback_url, document_id)
        raise
    except ValueError as e:
        logger.error(f"Value error during ingestion of document {document_id}: {e}")
        _send_failed_callback(callback_url, document_id)
        raise
    except NotImplementedError as e:
        logger.error(f"Feature not implemented for document {document_id}: {e}")
        _send_failed_callback(callback_url, document_id)
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during ingestion of document {document_id}: {e}",
            exc_info=True,
        )
        _send_failed_callback(callback_url, document_id)
        raise


def _send_failed_callback(callback_url: Optional[str], document_id: int):
    """Send failed status callback if callback_url is provided."""
    if callback_url:
        _send_callback_with_retry(
            callback_url,
            {
                "document_id": document_id,
                "status": "failed",
            },
            document_id,
        )


def _send_callback_with_retry(callback_url: str, payload: dict, document_id: int, max_retries: int = 3):
    """
    Send callback with retry logic.

    Args:
        callback_url: URL to send callback to
        payload: JSON payload to send
        document_id: Document ID for logging
        max_retries: Maximum number of retry attempts
    """
    import httpx
    import socket
    from urllib.parse import urlparse

    logger.info(f"Attempting to send callback for document {document_id} to {callback_url}")

    # Parse URL to get hostname
    parsed = urlparse(callback_url)
    hostname = parsed.hostname

    # Test DNS resolution and connectivity
    try:
        ip = socket.gethostbyname(hostname)
        logger.debug(f"Resolved {hostname} to {ip}")
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed for {hostname}: {e}")
        return

    for attempt in range(max_retries):
        try:
            logger.debug(f"Sending callback attempt {attempt + 1}/{max_retries} for document {document_id}")
            response = httpx.post(
                callback_url,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info(f"Callback sent successfully for document {document_id} (attempt {attempt + 1})")
            return
        except httpx.ConnectError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                logger.warning(
                    f"Connection error sending callback for document {document_id} "
                    f"(attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"Failed to send callback for document {document_id} after {max_retries} attempts: {e}. "
                    f"URL: {callback_url}, Hostname: {hostname}, IP: {ip}"
                )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending callback for document {document_id}: {e}")
            return  # Don't retry on HTTP errors (4xx, 5xx)
        except Exception as e:
            logger.error(f"Unexpected error sending callback for document {document_id}: {e}")
            return  # Don't retry on unexpected errors
