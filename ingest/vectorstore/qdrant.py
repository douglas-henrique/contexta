import logging
import uuid
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..config import OPENAI_EMBEDDING_MODEL, QDRANT_COLLECTION, QDRANT_URL

logger = logging.getLogger(__name__)

client = QdrantClient(url=QDRANT_URL)

COLLECTION = QDRANT_COLLECTION

# Embedding dimensions for different models
EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


def _ensure_collection_exists():
    """Ensure the collection exists with correct configuration."""
    try:
        collection_list = client.get_collections().collections
        collection_names = [c.name for c in collection_list]

        if COLLECTION not in collection_names:
            dimension = EMBEDDING_DIMENSIONS.get(OPENAI_EMBEDDING_MODEL, 3072)
            logger.info(f"Creating collection {COLLECTION} with dimension {dimension}")

            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )
            logger.info(f"Collection {COLLECTION} created successfully")
        else:
            logger.debug(f"Collection {COLLECTION} already exists")
    except Exception as e:
        logger.error(f"Error ensuring collection exists: {e}")
        raise


def store_embeddings(
    document_id: int,
    chunks: List[str],
    embeddings: List[List[float]],
    metadata: dict,
    tenant_id: int,
):
    """
    Store embeddings in Qdrant with multi-tenant support.

    Args:
        document_id: ID of the document
        chunks: List of text chunks
        embeddings: List of embedding vectors
        metadata: Additional metadata
        tenant_id: Tenant identifier for multi-tenant isolation
    """
    _ensure_collection_exists()

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have the same length")

    points = []
    for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "tenant_id": tenant_id,
                    "text": chunk,
                    "chunk_index": idx,
                    **metadata,
                },
            )
        )

    try:
        client.upsert(collection_name=COLLECTION, points=points)
        logger.info(
            f"Stored {len(points)} chunks for document {document_id} (tenant {tenant_id})"
        )
    except Exception as e:
        logger.error(f"Error storing embeddings: {e}")
        raise


def search(
    query_embedding: List[float],
    tenant_id: int,
    top_k: int = 10,
    filters: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar documents in Qdrant with tenant filtering.

    Args:
        query_embedding: Query embedding vector
        tenant_id: Tenant identifier for filtering
        top_k: Number of results to return
        filters: Additional metadata filters

    Returns:
        List of search results with scores and metadata
    """
    _ensure_collection_exists()

    # Build filter conditions
    conditions = [FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]

    # Add additional filters if provided
    if filters:
        for key, value in filters.items():
            conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

    query_filter = Filter(must=conditions) if conditions else None

    try:
        results = client.search(
            collection_name=COLLECTION,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k,
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
                "text": result.payload.get("text", ""),
                "document_id": result.payload.get("document_id"),
                "chunk_index": result.payload.get("chunk_index"),
            }
            for result in results
        ]
    except Exception as e:
        logger.error(f"Error searching in Qdrant: {e}")
        raise
