"""
Pytest fixtures and configuration.
"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock = Mock()
    mock.chat.completions.create.return_value = Mock(
        choices=[
            Mock(message=Mock(content="This is a test response"))
        ]
    )
    mock.embeddings.create.return_value = Mock(
        data=[
            Mock(embedding=[0.1] * 3072),
            Mock(embedding=[0.2] * 3072)
        ]
    )
    return mock


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client."""
    mock = Mock()
    mock.get_collections.return_value = Mock(collections=[])
    mock.search.return_value = [
        Mock(
            id="test-id-1",
            score=0.95,
            payload={
                "text": "Test chunk 1",
                "document_id": 1,
                "chunk_index": 0,
                "tenant_id": 1
            }
        ),
        Mock(
            id="test-id-2",
            score=0.85,
            payload={
                "text": "Test chunk 2",
                "document_id": 1,
                "chunk_index": 1,
                "tenant_id": 1
            }
        )
    ]
    return mock


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample document for testing.
    It contains multiple sentences and paragraphs.
    
    The purpose is to test chunking and embedding functionality.
    This should be sufficient for basic unit tests.
    """


@pytest.fixture
def sample_chunks():
    """Sample chunks for testing."""
    return [
        "This is a sample document for testing.",
        "It contains multiple sentences and paragraphs.",
        "The purpose is to test chunking and embedding functionality."
    ]


@pytest.fixture
def sample_embeddings():
    """Sample embeddings for testing."""
    return [
        [0.1] * 3072,
        [0.2] * 3072,
        [0.3] * 3072
    ]


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "id": "test-1",
            "score": 0.95,
            "text": "Test result 1",
            "document_id": 1,
            "chunk_index": 0,
            "payload": {"metadata": "test"}
        },
        {
            "id": "test-2",
            "score": 0.85,
            "text": "Test result 2",
            "document_id": 1,
            "chunk_index": 1,
            "payload": {"metadata": "test"}
        }
    ]

