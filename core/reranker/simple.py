"""
Simple re-ranking implementation based on scores.
"""

from typing import Any, Dict, List

from .base import Reranker


class SimpleReranker(Reranker):
    """
    Simple re-ranker that sorts by score.

    This is a basic implementation that can be replaced with
    more sophisticated re-ranking (CrossEncoder, LLM-based, etc.)
    """

    def rerank(self, query: str, results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Re-rank results by score (descending).

        Args:
            query: Original query text (not used in simple reranking)
            results: List of search results
            top_k: Number of top results to return

        Returns:
            Re-ranked list of results sorted by score
        """
        # Sort by score (descending) and return top_k
        sorted_results = sorted(results, key=lambda x: x.get("score", 0.0), reverse=True)

        return sorted_results[:top_k]
