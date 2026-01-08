import logging
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

from ingest.tasks import ingest_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Contexta Ingest Service")


class IngestRequest(BaseModel):
    document_id: int
    file_path: str
    tenant_id: int
    metadata: dict = {}
    callback_url: Optional[str] = None


@app.post("/ingest")
def ingest(payload: IngestRequest, background_tasks: BackgroundTasks):
    """Trigger document ingestion in background."""
    try:
        background_tasks.add_task(
            ingest_document,
            payload.document_id,
            payload.file_path,
            payload.metadata,
            payload.tenant_id,
            payload.callback_url,
        )

        logger.info(f"Ingestion task queued for document {payload.document_id} (tenant {payload.tenant_id})")

        return {
            "status": "accepted",
            "document_id": payload.document_id,
            "tenant_id": payload.tenant_id,
        }
    except Exception as e:
        logger.error(f"Error queuing ingestion task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check endpoint."""
    try:
        from ingest.vectorstore.qdrant import COLLECTION, client

        # Check Qdrant connection
        _ = client.get_collections()  # noqa: F841
        return {"status": "ok", "qdrant": "connected", "collection": COLLECTION}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "error": str(e)}
