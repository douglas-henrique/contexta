import logging
from pathlib import Path
from typing import Optional
from ingest.loaders.pdf import load_pdf
from ingest.chunking.semantic import semantic_chunk
from ingest.embeddings.openai import embed_texts
from ingest.vectorstore.qdrant import store_embeddings

logger = logging.getLogger(__name__)


def _detect_file_type(file_path: str) -> str:
    """Detect file type from extension."""
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == '.pdf':
        return 'pdf'
    elif extension in ['.txt', '.text']:
        return 'txt'
    elif extension == '.docx':
        return 'docx'
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
    if file_type == 'pdf':
        return load_pdf(file_path)
    elif file_type == 'txt':
        return _load_txt(file_path)
    elif file_type == 'docx':
        raise NotImplementedError("DOCX loading not yet implemented")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def ingest_document(
    document_id: int,
    file_path: str,
    metadata: dict,
    tenant_id: int,
    callback_url: Optional[str] = None
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
            tenant_id=tenant_id
        )
        
        logger.info(f"Document {document_id} ingested successfully (tenant {tenant_id})")
        
        # 5. Callback if provided
        if callback_url:
            try:
                import httpx
                httpx.post(callback_url, json={
                    "document_id": document_id,
                    "status": "completed",
                    "chunks_created": len(chunks)
                }, timeout=5.0)
            except Exception as e:
                logger.warning(f"Failed to send callback: {e}")
        
    except FileNotFoundError as e:
        logger.error(f"File not found for document {document_id}: {e}")
        raise
    except ValueError as e:
        logger.error(f"Value error during ingestion of document {document_id}: {e}")
        raise
    except NotImplementedError as e:
        logger.error(f"Feature not implemented for document {document_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ingestion of document {document_id}: {e}", exc_info=True)
        raise
