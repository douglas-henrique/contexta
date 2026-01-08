"""
Base interface for embedding generators.
"""

from abc import ABC, abstractmethod
from typing import List


class Embedder(ABC):
    """Abstract base class for embedding generators."""
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this embedder.
        
        Returns:
            Dimension of the embedding vector
        """
        pass

