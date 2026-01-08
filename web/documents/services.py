"""
Services for document management and ingestion.
"""

import logging
from typing import Optional

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


def trigger_ingestion(
    document_id: int,
    file_path: str,
    user_id: int,
    metadata: Optional[dict] = None,
    callback_url: Optional[str] = None
) -> bool:
    """
    Trigger document ingestion in the ingest service.

    Args:
        document_id: ID of the document to ingest
        file_path: Path to the document file
        user_id: ID of the user (used as tenant_id)
        metadata: Optional metadata dictionary
        callback_url: Optional callback URL for status updates

    Returns:
        True if ingestion was triggered successfully, False otherwise
    """
    ingest_service_url = getattr(settings, 'INGEST_SERVICE_URL', 'http://localhost:8001')
    url = f"{ingest_service_url}/ingest"

    payload = {
        "document_id": document_id,
        "file_path": file_path,
        "tenant_id": user_id,
        "metadata": metadata or {},
    }

    if callback_url:
        payload["callback_url"] = callback_url

    try:
        logger.info(f"Triggering ingestion for document {document_id} (tenant {user_id})")

        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("status") == "accepted":
                logger.info(f"Ingestion triggered successfully for document {document_id}")
                return True
            else:
                logger.warning(f"Unexpected response from ingest service: {result}")
                return False

    except httpx.HTTPError as e:
        logger.error(f"HTTP error triggering ingestion for document {document_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error triggering ingestion for document {document_id}: {e}", exc_info=True)
        return False
