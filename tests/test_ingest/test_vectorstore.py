"""
Tests for vector store implementations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ingest.vectorstore.qdrant import store_embeddings, search, _ensure_collection_exists


class TestQdrantVectorStore:
    """Tests for Qdrant vector store."""
    
    @patch('ingest.vectorstore.qdrant.client')
    def test_ensure_collection_exists_creates_new(self, mock_client):
        """Test collection creation when it doesn't exist."""
        # Mock: collection doesn't exist
        mock_client.get_collections.return_value = Mock(collections=[])
        
        _ensure_collection_exists()
        
        mock_client.create_collection.assert_called_once()
    
    @patch('ingest.vectorstore.qdrant.client')
    def test_ensure_collection_exists_skips_existing(self, mock_client):
        """Test skips creation when collection exists."""
        # Mock: collection already exists
        mock_collection = Mock()
        mock_collection.name = "contexta_documents"
        mock_client.get_collections.return_value = Mock(
            collections=[mock_collection]
        )
        
        _ensure_collection_exists()
        
        mock_client.create_collection.assert_not_called()
    
    @patch('ingest.vectorstore.qdrant.client')
    @patch('ingest.vectorstore.qdrant._ensure_collection_exists')
    def test_store_embeddings(self, mock_ensure, mock_client):
        """Test storing embeddings."""
        chunks = ["chunk1", "chunk2"]
        embeddings = [[0.1] * 3072, [0.2] * 3072]
        metadata = {"source": "test"}
        tenant_id = 1
        
        store_embeddings(
            document_id=1,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
            tenant_id=tenant_id
        )
        
        mock_ensure.assert_called_once()
        mock_client.upsert.assert_called_once()
        
        # Check the points were created correctly
        call_args = mock_client.upsert.call_args
        points = call_args[1]['points']
        
        assert len(points) == 2
        assert all(p.payload['tenant_id'] == tenant_id for p in points)
        assert all(p.payload['document_id'] == 1 for p in points)
    
    @patch('ingest.vectorstore.qdrant.client')
    @patch('ingest.vectorstore.qdrant._ensure_collection_exists')
    def test_store_embeddings_mismatch(self, mock_ensure, mock_client):
        """Test storing embeddings with mismatched lengths."""
        chunks = ["chunk1", "chunk2"]
        embeddings = [[0.1] * 3072]  # Only one embedding
        
        with pytest.raises(ValueError, match="same length"):
            store_embeddings(
                document_id=1,
                chunks=chunks,
                embeddings=embeddings,
                metadata={},
                tenant_id=1
            )
    
    @patch('ingest.vectorstore.qdrant.client')
    @patch('ingest.vectorstore.qdrant._ensure_collection_exists')
    def test_search(self, mock_ensure, mock_client):
        """Test vector search."""
        # Mock search results
        mock_client.search.return_value = [
            Mock(
                id="id1",
                score=0.95,
                payload={
                    "text": "Result 1",
                    "document_id": 1,
                    "chunk_index": 0,
                    "tenant_id": 1
                }
            ),
            Mock(
                id="id2",
                score=0.85,
                payload={
                    "text": "Result 2",
                    "document_id": 1,
                    "chunk_index": 1,
                    "tenant_id": 1
                }
            )
        ]
        
        query_embedding = [0.1] * 3072
        results = search(
            query_embedding=query_embedding,
            tenant_id=1,
            top_k=10
        )
        
        assert len(results) == 2
        assert results[0]["score"] == 0.95
        assert results[0]["text"] == "Result 1"
        assert results[1]["score"] == 0.85
        
        mock_ensure.assert_called_once()
        mock_client.search.assert_called_once()
    
    @patch('ingest.vectorstore.qdrant.client')
    @patch('ingest.vectorstore.qdrant._ensure_collection_exists')
    def test_search_with_filters(self, mock_ensure, mock_client):
        """Test search with additional filters."""
        mock_client.search.return_value = []
        
        query_embedding = [0.1] * 3072
        search(
            query_embedding=query_embedding,
            tenant_id=1,
            top_k=5,
            filters={"document_id": 123}
        )
        
        call_args = mock_client.search.call_args
        query_filter = call_args[1]['query_filter']
        
        # Should have filters for both tenant_id and document_id
        assert query_filter is not None

