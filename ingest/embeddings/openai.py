import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Lazy initialization - client is created only when needed
_client = None


def _get_client() -> OpenAI:
    """Get or create OpenAI client with lazy initialization."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        _client = OpenAI(api_key=api_key)
    return _client


def embed_texts(texts: list[str]):
    """Generate embeddings for a list of texts using OpenAI API."""
    client = _get_client()
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    response = client.embeddings.create(model=embedding_model, input=texts)
    return [e.embedding for e in response.data]
