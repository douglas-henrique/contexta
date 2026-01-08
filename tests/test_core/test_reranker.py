"""
Tests for re-ranking strategies.
"""

import pytest
from core.reranker.simple import SimpleReranker


class TestSimpleReranker:
    """Tests for simple re-ranker."""
    
    def test_rerank_by_score(self):
        """Test re-ranking by score."""
        reranker = SimpleReranker()
        
        results = [
            {"text": "Result 1", "score": 0.7},
            {"text": "Result 2", "score": 0.9},
            {"text": "Result 3", "score": 0.5}
        ]
        
        reranked = reranker.rerank("test query", results, top_k=3)
        
        assert len(reranked) == 3
        assert reranked[0]["score"] == 0.9
        assert reranked[1]["score"] == 0.7
        assert reranked[2]["score"] == 0.5
    
    def test_rerank_top_k(self):
        """Test re-ranking returns only top_k results."""
        reranker = SimpleReranker()
        
        results = [
            {"text": f"Result {i}", "score": i * 0.1}
            for i in range(10)
        ]
        
        reranked = reranker.rerank("test query", results, top_k=3)
        
        assert len(reranked) == 3
        assert reranked[0]["score"] >= reranked[1]["score"]
        assert reranked[1]["score"] >= reranked[2]["score"]
    
    def test_rerank_with_missing_scores(self):
        """Test re-ranking with missing scores."""
        reranker = SimpleReranker()
        
        results = [
            {"text": "Result 1", "score": 0.8},
            {"text": "Result 2"},  # No score
            {"text": "Result 3", "score": 0.9}
        ]
        
        reranked = reranker.rerank("test query", results, top_k=3)
        
        # Result with no score should be treated as 0.0
        assert len(reranked) == 3
        assert reranked[0]["score"] == 0.9
        assert reranked[1]["score"] == 0.8
        assert reranked[2].get("score", 0.0) == 0.0
    
    def test_rerank_empty_results(self):
        """Test re-ranking with empty results."""
        reranker = SimpleReranker()
        
        reranked = reranker.rerank("test query", [], top_k=5)
        
        assert reranked == []

