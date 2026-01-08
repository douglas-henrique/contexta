# Contexta

Production-grade RAG (Retrieval-Augmented Generation) SaaS application.

> 📚 **Documentação Completa**: Veja [project_docs/](project_docs/) para guias detalhados de Docker, testes, arquitetura e mais.

## Architecture

Contexta follows a clean architecture with strict separation of concerns:

- **Django (web/)**: Handles authentication, multi-tenancy, document metadata, file uploads, and admin interface
- **FastAPI (api/ & ingest/)**: Handles RAG pipeline, retrieval, re-ranking, and LLM calls
- **Core (core/)**: Framework-agnostic domain logic, interfaces, and abstractions

## Project Structure

```
contexta/
 ├── pyproject.toml
 ├── README.md
 ├── .env.example
 ├── core/              # Framework-agnostic core logic
 │   ├── llm/           # LLM provider abstractions
 │   ├── prompts/       # Prompt builders
 │   ├── reranker/      # Re-ranking strategies
 │   └── ...
 ├── api/               # FastAPI - Query/Retrieval service
 ├── ingest/            # FastAPI - Document ingestion service
 │   ├── loaders/       # Document loaders (PDF, TXT, DOCX)
 │   ├── chunking/      # Text chunking strategies
 │   ├── embeddings/    # Embedding generators
 │   └── vectorstore/   # Vector store implementations
 └── web/               # Django - Product backend
     └── documents/     # Document management
```

## Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Qdrant (vector database) - running on localhost:6333 by default
- OpenAI API key
- Docker & Docker Compose (optional, para rodar com containers)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd contexta
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your configuration
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_URL`: Qdrant server URL (default: http://localhost:6333)
- `INGEST_SERVICE_URL`: Ingest service URL (default: http://localhost:8001)
- `DJANGO_SECRET_KEY`: Django secret key (for production)

## Running the Services

### 1. Start Qdrant

Using Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

Or install Qdrant locally following [Qdrant documentation](https://qdrant.tech/documentation/).

### 2. Run Django (Web Backend)

```bash
cd web
python manage.py migrate
python manage.py createsuperuser  # Create admin user
python manage.py runserver
```

Django will run on `http://localhost:8000`

### 3. Run Ingest Service

```bash
uvicorn ingest.main:app --reload --port 8001
```

Ingest service will run on `http://localhost:8001`

### 4. Run Query API Service

```bash
uvicorn api.main:app --reload --port 8000
```

Query API will run on `http://localhost:8000` (or different port if Django is running)

## Usage

### Upload and Ingest Documents

1. **Via Django Admin:**
   - Access `http://localhost:8000/admin`
   - Login with superuser credentials
   - Upload documents through the admin interface

2. **Via Django REST API:**
```bash
# Authenticate first
curl -X POST http://localhost:8000/api/auth/login/ \
  -d "username=your_username&password=your_password"

# Upload document
curl -X POST http://localhost:8000/api/documents/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=My Document" \
  -F "file=@/path/to/document.pdf"
```

The document will be automatically processed:
- Status: `pending` → `processing` → `completed` (or `failed` on error)

### Query Documents

Query the RAG system:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the documents?",
    "tenant_id": 1,
    "top_k": 10,
    "rerank_top_k": 5
  }'
```

Response:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "document_id": 1,
      "chunk_index": 0,
      "score": 0.95,
      "text_preview": "..."
    }
  ],
  "query": "What is the main topic?",
  "tenant_id": 1
}
```

## API Endpoints

### Query API (`api/main.py`)

- `POST /query`: Query documents using RAG
- `GET /health`: Health check

### Ingest Service (`ingest/main.py`)

- `POST /ingest`: Trigger document ingestion
- `GET /health`: Health check

### Django API (`web/documents/`)

- `GET /api/documents/`: List documents
- `POST /api/documents/`: Upload document
- `GET /api/documents/{id}/`: Get document details
- `PUT /api/documents/{id}/`: Update document
- `DELETE /api/documents/{id}/`: Delete document

## Development

### Running Tests

```bash
# Run Django tests
cd web
python manage.py test

# Run API tests (when implemented)
pytest api/tests/
```

### Code Style

This project follows:
- Type hints everywhere
- Clean architecture principles
- Separation of concerns
- Framework-agnostic core logic

### Adding New Features

1. **New Document Loader**: Add to `ingest/loaders/`
2. **New LLM Provider**: Implement `core/llm/base.py` interface
3. **New Re-ranker**: Implement `core/reranker/base.py` interface
4. **New Vector Store**: Implement `ingest/vectorstore/base.py` interface

## Architecture Principles

- **Multi-tenancy**: All queries filter by `tenant_id` (user.id)
- **LLM Abstraction**: Never call OpenAI directly - use `core/llm/` interfaces
- **Prompt Builder**: Use `core/prompts/` for all prompt construction
- **Error Handling**: Comprehensive logging and error handling throughout
- **Type Safety**: Type hints required for all functions

## Tests

Contexta has a complete suite of unit and integration tests.

### Quick Start

```bash
# All tests
./run_tests.sh

# Tests with coverage
./run_tests.sh cov

# Only unit tests
./run_tests.sh unit
```

### Complete Testing Documentation

📚 **[Visual Testing Guide](project_docs/TESTING_GUIDE.md)** - Complete guide with structure, best practices, CI/CD and troubleshooting

📖 **[Detailed Documentation](project_docs/README_TESTS.md)** - Fixtures, examples, configuration and integration

## Troubleshooting

### Qdrant Connection Issues

- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check `QDRANT_URL` in `.env`
- If using Docker: `docker-compose ps` to see container status

### OpenAI API Issues

- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key validity and quota
- Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### Document Ingestion Fails

- Check ingest service logs: `docker-compose logs ingest`
- Verify file path is accessible
- Check document format is supported (PDF, TXT)
- Verify tenant_id is correct

### Import Errors in Tests

```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
poetry run pytest
```

### Outdated Dependencies

```bash
# Update poetry.lock
poetry lock

# Reinstall dependencies
poetry install --no-root
```

## Docker

### Quick Start with Docker

```bash
# Start all services
make up

# View logs
make logs

# Run tests
make docker-test

# Stop services
make down
```

📚 **[Complete Docker Documentation](project_docs/DOCKER_README.md)** - Detailed guide on setup, troubleshooting and Docker commands

## License

MIT License

