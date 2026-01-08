"""
Tests for main API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from api.main import app


client = TestClient(app)


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "version" in data
    
    @patch('api.main.client')
    def test_health_endpoint(self, mock_qdrant_client):
        """Test health check endpoint."""
        mock_qdrant_client.get_collections.return_value = Mock(collections=[])
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @patch('api.main.llm')
    @patch('api.main.reranker')
    @patch('ingest.vectorstore.qdrant.search')
    @patch('ingest.embeddings.openai.embed_texts')
    def test_query_endpoint(
        self,
        mock_embed,
        mock_search,
        mock_reranker,
        mock_llm
    ):
        """Test query endpoint."""
        # Setup mocks
        mock_embed.return_value = [[0.1] * 3072]
        mock_search.return_value = [
            {
                "id": "test-1",
                "score": 0.95,
                "text": "Test result",
                "document_id": 1,
                "chunk_index": 0,
                "payload": {}
            }
        ]
        mock_reranker.rerank.return_value = mock_search.return_value
        mock_llm.generate.return_value = "This is a test answer"
        
        # Make request
        response = client.post(
            "/query",
            json={
                "query": "What is a test?",
                "tenant_id": 1,
                "top_k": 10,
                "rerank_top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "query" in data
        assert data["answer"] == "This is a test answer"
    
    @patch('ingest.vectorstore.qdrant.search')
    @patch('ingest.embeddings.openai.embed_texts')
    def test_query_endpoint_no_results(self, mock_embed, mock_search):
        """Test query endpoint with no search results."""
        mock_embed.return_value = [[0.1] * 3072]
        mock_search.return_value = []
        
        response = client.post(
            "/query",
            json={
                "query": "Test query",
                "tenant_id": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "couldn't find" in data["answer"].lower()
        assert len(data["sources"]) == 0
    
    def test_query_endpoint_validation(self):
        """Test query endpoint validates input."""
        # Missing required fields
        response = client.post(
            "/query",
            json={"query": "Test"}  # Missing tenant_id
        )
        
        assert response.status_code == 422  # Validation error

