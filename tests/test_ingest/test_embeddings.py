"""
Tests for embedding generators.
"""

import pytest
from unittest.mock import Mock, patch
from ingest.embeddings.openai import embed_texts


class TestOpenAIEmbeddings:
    """Tests for OpenAI embeddings."""
    
    @patch('ingest.embeddings.openai.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_embed_texts(self, mock_openai_class):
        """Test embedding generation."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 3072),
            Mock(embedding=[0.2] * 3072)
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Patch the module-level client
        with patch('ingest.embeddings.openai.client', mock_client):
            texts = ["text 1", "text 2"]
            embeddings = embed_texts(texts)
            
            assert len(embeddings) == 2
            assert len(embeddings[0]) == 3072
            assert len(embeddings[1]) == 3072
            
            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-3-large",
                input=texts
            )
    
    @patch('ingest.embeddings.openai.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_EMBEDDING_MODEL': 'text-embedding-3-small'})
    def test_embed_texts_custom_model(self, mock_openai_class):
        """Test embedding with custom model."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch('ingest.embeddings.openai.client', mock_client):
            with patch('ingest.embeddings.openai.EMBEDDING_MODEL', 'text-embedding-3-small'):
                embeddings = embed_texts(["test"])
                
                assert len(embeddings) == 1

