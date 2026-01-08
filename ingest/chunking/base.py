"""
Base interface for chunking strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models import Chunk


class Chunker(ABC):
    """Abstract base class for chunking strategies."""
    
    @abstractmethod
    async def chunk(
        self,
        content: str,
        document_id: int,
        tenant_id: str,
        metadata: Dict[str, Any],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Chunk]:
        """
        Split content into chunks.
        
        Args:
            content: Text content to chunk
            document_id: ID of the source document
            tenant_id: Tenant identifier for multi-tenancy
            metadata: Additional metadata to attach to chunks
            chunk_size: Target size for each chunk (in characters or tokens)
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of Chunk objects
        """
        pass

