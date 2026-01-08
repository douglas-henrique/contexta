"""
Tests for prompt builders.
"""

import pytest
from core.prompts.rag import RAGPromptBuilder


class TestRAGPromptBuilder:
    """Tests for RAG prompt builder."""
    
    def test_initialization(self):
        """Test prompt builder initialization."""
        builder = RAGPromptBuilder()
        
        assert builder.context_prefix == "Context:"
        assert builder.question_prefix == "Question:"
        assert builder.answer_prefix == "Answer:"
        assert builder.system_instruction is not None
    
    def test_custom_initialization(self):
        """Test prompt builder with custom parameters."""
        builder = RAGPromptBuilder(
            system_instruction="Custom instruction",
            context_prefix="CTX:",
            question_prefix="Q:",
            answer_prefix="A:"
        )
        
        assert builder.system_instruction == "Custom instruction"
        assert builder.context_prefix == "CTX:"
        assert builder.question_prefix == "Q:"
        assert builder.answer_prefix == "A:"
    
    def test_build_basic(self):
        """Test basic prompt building."""
        builder = RAGPromptBuilder()
        
        context_chunks = [
            {"text": "First chunk of information."},
            {"text": "Second chunk of information."}
        ]
        
        prompt = builder.build(
            question="What is the test?",
            context_chunks=context_chunks
        )
        
        assert "Context:" in prompt
        assert "Question: What is the test?" in prompt
        assert "Answer:" in prompt
        assert "First chunk of information." in prompt
        assert "Second chunk of information." in prompt
    
    def test_build_with_max_length(self):
        """Test prompt building respects max context length."""
        builder = RAGPromptBuilder()
        
        long_text = "A" * 2000
        context_chunks = [
            {"text": long_text},
            {"text": "This should not appear"}
        ]
        
        prompt = builder.build(
            question="Test",
            context_chunks=context_chunks,
            max_context_length=1500
        )
        
        # Second chunk should be excluded due to length limit
        assert "This should not appear" not in prompt
    
    def test_build_with_sources(self):
        """Test prompt building with source citations."""
        builder = RAGPromptBuilder()
        
        context_chunks = [
            {
                "text": "Information from document 1.",
                "document_id": 1,
                "chunk_index": 0
            },
            {
                "text": "Information from document 2.",
                "document_id": 2,
                "chunk_index": 1
            }
        ]
        
        prompt = builder.build_with_sources(
            question="What is the test?",
            context_chunks=context_chunks,
            include_sources=True
        )
        
        assert "[Source: Document 1, Chunk 0]" in prompt
        assert "[Source: Document 2, Chunk 1]" in prompt
    
    def test_build_with_empty_chunks(self):
        """Test prompt building with empty chunks."""
        builder = RAGPromptBuilder()
        
        prompt = builder.build(
            question="Test question",
            context_chunks=[]
        )
        
        assert "Question: Test question" in prompt
        assert "Answer:" in prompt

