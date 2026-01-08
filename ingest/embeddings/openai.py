import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=api_key)

EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')


def embed_texts(texts: list[str]):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [e.embedding for e in response.data]
