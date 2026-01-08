# Contexta

RAG application

## Project Structure

```
contexta/
 ├── pyproject.toml
 ├── README.md
 ├── .gitignore
 ├── .env
 ├── core/
 │   ├── llm/
 │   ├── embeddings/
 │   ├── vector_store/
 │   ├── search/
 │   ├── reranker/
 │   ├── chunking/
 │   ├── prompts/
 │   └── rag/
 ├── api/        # FastAPI
 ├── web/        # Django
 └── workers/    # Celery
```

## Installation

```bash
pip install -e .
```

## Development

```bash
# Install dependencies
poetry install

# Run development server
poetry run python -m api.main
```

