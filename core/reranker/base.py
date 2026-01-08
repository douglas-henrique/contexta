"""
Base interface for re-ranking strategies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Reranker(ABC):
    """Abstract base class for re-ranking strategies."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results based on query relevance.

        Args:
            query: Original query text
            results: List of search results with 'text', 'score', and metadata
            top_k: Number of top results to return

        Returns:
            Re-ranked list of results
        """
        pass
