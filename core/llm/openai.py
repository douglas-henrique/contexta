"""
OpenAI LLM provider implementation.
"""

import os
from typing import Optional
from openai import OpenAI
from .base import LLMProvider


class OpenAILLM(LLMProvider):
    """
    OpenAI LLM provider implementation.
    
    This class abstracts OpenAI API calls to allow for
    future replacement with other providers.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize OpenAI LLM provider.
        
        Args:
            model: OpenAI model name (e.g., "gpt-4o-mini", "gpt-4o")
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            temperature: Default temperature for generation
            max_tokens: Default max tokens for generation
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion from a prompt.
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI API parameters
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens or self.default_max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e
    
    def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Generate text completion with streaming.
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI API parameters
            
        Yields:
            Text chunks as they are generated
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens or self.default_max_tokens,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API streaming error: {e}") from e
    
    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        return self.model

