"""
Embedding generators for text vectorization.
"""

from .base import Embedder
from .openai import embed_texts

__all__ = ["Embedder", "embed_texts"]
