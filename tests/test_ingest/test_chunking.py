"""
Tests for chunking strategies.
"""

import pytest
from ingest.chunking.semantic import semantic_chunk


class TestSemanticChunking:
    """Tests for semantic chunking."""
    
    def test_basic_chunking(self):
        """Test basic text chunking."""
        text = "word " * 1000  # 1000 words
        
        chunks = semantic_chunk(text, max_tokens=100, overlap=10)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    def test_chunk_size(self):
        """Test chunks respect max_tokens."""
        text = "word " * 1000
        
        chunks = semantic_chunk(text, max_tokens=50, overlap=0)
        
        for chunk in chunks:
            word_count = len(chunk.split())
            assert word_count <= 50
    
    def test_chunk_overlap(self):
        """Test chunk overlap."""
        text = "word " * 200
        
        chunks = semantic_chunk(text, max_tokens=50, overlap=10)
        
        # With overlap, we should have more chunks than without
        chunks_no_overlap = semantic_chunk(text, max_tokens=50, overlap=0)
        assert len(chunks) >= len(chunks_no_overlap)
    
    def test_short_text(self):
        """Test chunking with text shorter than max_tokens."""
        text = "This is a short text."
        
        chunks = semantic_chunk(text, max_tokens=100)
        
        assert len(chunks) == 1
        assert chunks[0] == text.strip()
    
    def test_empty_text(self):
        """Test chunking with empty text."""
        chunks = semantic_chunk("", max_tokens=100)
        
        assert len(chunks) == 1
        assert chunks[0] == ""

