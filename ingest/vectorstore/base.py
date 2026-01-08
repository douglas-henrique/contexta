"""
Base interface for vector stores.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models import Chunk


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def add_documents(self, chunks: List[Chunk], embeddings: List[List[float]], tenant_id: str) -> None:
        """
        Add documents to the vector store.

        Args:
            chunks: List of chunk objects
            embeddings: List of embedding vectors (one per chunk)
            tenant_id: Tenant identifier for multi-tenant isolation
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        tenant_id: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            tenant_id: Tenant identifier for filtering
            top_k: Number of results to return
            filters: Additional metadata filters

        Returns:
            List of search results with scores and metadata
        """
        pass

    @abstractmethod
    async def delete_document(self, document_id: int, tenant_id: str) -> None:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID to delete
            tenant_id: Tenant identifier
        """
        pass

    @abstractmethod
    async def get_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get statistics about stored documents.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Dictionary with statistics
        """
        pass
