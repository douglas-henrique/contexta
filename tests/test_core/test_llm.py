"""
Tests for LLM abstractions.
"""

import pytest
from unittest.mock import Mock, patch
from core.llm.openai import OpenAILLM


class TestOpenAILLM:
    """Tests for OpenAI LLM provider."""
    
    @patch('core.llm.openai.OpenAI')
    def test_initialization(self, mock_openai_class):
        """Test LLM initialization."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            llm = OpenAILLM(model="gpt-4o-mini")
            
            assert llm.model == "gpt-4o-mini"
            assert llm.api_key == "test-key"
            mock_openai_class.assert_called_once_with(api_key="test-key")
    
    def test_initialization_without_api_key(self):
        """Test LLM initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                OpenAILLM()
    
    @patch('core.llm.openai.OpenAI')
    def test_generate(self, mock_openai_class):
        """Test text generation."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            llm = OpenAILLM()
            result = llm.generate("Test prompt")
            
            assert result == "Generated text"
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('core.llm.openai.OpenAI')
    def test_generate_with_parameters(self, mock_openai_class):
        """Test text generation with custom parameters."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            llm = OpenAILLM()
            result = llm.generate(
                "Test prompt",
                temperature=0.5,
                max_tokens=100
            )
            
            assert result == "Generated text"
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['temperature'] == 0.5
            assert call_args[1]['max_tokens'] == 100
    
    @patch('core.llm.openai.OpenAI')
    def test_generate_stream(self, mock_openai_class):
        """Test streaming text generation."""
        mock_client = Mock()
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))]),
            Mock(choices=[Mock(delta=Mock(content=" world"))]),
            Mock(choices=[Mock(delta=Mock(content="!"))])
        ]
        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            llm = OpenAILLM()
            result = list(llm.generate_stream("Test prompt"))
            
            assert result == ["Hello", " world", "!"]
    
    @patch('core.llm.openai.OpenAI')
    def test_get_model_name(self, mock_openai_class):
        """Test get model name."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            llm = OpenAILLM(model="gpt-4o")
            assert llm.get_model_name() == "gpt-4o"

