# 🏗️ Contexta Architecture

> **Status:** ✅ Complete

## Overview

Contexta is a RAG (Retrieval-Augmented Generation) SaaS application built with clean architecture and strict separation of concerns.

## High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│                    [Separate - not implemented]                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Web Backend                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Authentication & Authorization                          │  │
│  │ • Multi-tenancy Management                               │  │
│  │ • Document Metadata & Upload                             │  │
│  │ • Billing & Usage Tracking                               │  │
│  │ • Admin Interface                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────┬─────────────────────────────────────┬───────────────┘
            │                                     │
            │ Trigger Ingest                      │ Query API
            ▼                                     ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│  Ingest Service (FastAPI)│        │   Query API (FastAPI)    │
│  ┌────────────────────┐  │        │  ┌────────────────────┐ │
│  │ • Document Loading │  │        │  │ • Query Embedding  │ │
│  │ • Text Chunking    │  │        │  │ • Vector Search    │ │
│  │ • Embedding Gen    │  │        │  │ • Re-ranking       │ │
│  │ • Vector Storage   │  │        │  │ • Prompt Building  │ │
│  └────────────────────┘  │        │  │ • LLM Generation   │ │
└───────────┬──────────────┘        │  └────────────────────┘ │
            │                       └────────┬─────────────────┘
            │                                │
            ▼                                ▼
┌────────────────────────────────────────────────────────────────┐
│                        Core (Framework-agnostic)                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ • LLM Abstractions (OpenAI, Ollama, etc.)                │ │
│  │ • Prompt Builders                                         │ │
│  │ • Re-ranking Strategies                                   │ │
│  │ • Domain Logic                                            │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
            │                                │
            ▼                                ▼
┌──────────────────────┐        ┌──────────────────────────┐
│   Qdrant (Vectors)   │        │   OpenAI API (LLM)       │
│  • Embeddings        │        │  • Chat Completions      │
│  • Similarity Search │        │  • Embeddings            │
└──────────────────────┘        └──────────────────────────┘
```

## Main Components

### 1. Django Web Backend (`web/`)

**Responsibilities:**
- User authentication and authorization
- Multi-tenancy management (tenant_id = user.id)
- Document metadata CRUD
- File upload and storage
- Usage tracking and billing
- Administrative interface

**Technologies:**
- Django 6.x
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod)
- Django Admin

**Main Endpoints:**
- `/admin/` - Administrative interface
- `/api/documents/` - Document CRUD
- `/api/users/` - User management

### 2. Ingest Service (`ingest/`)

**Responsibilities:**
- Load documents (PDF, TXT, DOCX)
- Semantic text chunking
- Generate embeddings (OpenAI)
- Store in vector store (Qdrant)
- Asynchronous background processing

**Technologies:**
- FastAPI
- pypdf (PDF loading)
- OpenAI API (embeddings)
- Qdrant Client
- Background Tasks

**Endpoints:**
- `POST /ingest` - Trigger document ingestion
- `GET /health` - Health check

**Flow:**
```
Document Upload → Load → Chunk → Embed → Store in Qdrant
```

### 3. Query API Service (`api/`)

**Responsibilities:**
- Receive user queries
- Generate query embeddings
- Search similar documents (vector search)
- Re-rank results
- Build prompts with context
- Generate responses using LLM

**Technologies:**
- FastAPI
- OpenAI API (chat completions)
- Qdrant Client

**Endpoints:**
- `POST /query` - Process RAG query
- `GET /health` - Health check

**Flow:**
```
User Query → Embed → Search → Rerank → Prompt → LLM → Response
```

### 4. Core Package (`core/`)

**Responsibilities:**
- LLM abstractions (provider-agnostic)
- Prompt builders
- Re-ranking strategies
- Pure domain logic

**Principles:**
- ✅ Framework-agnostic (no Django, no FastAPI)
- ✅ Testable in isolation
- ✅ Dependency Injection
- ✅ Clear interfaces

**Modules:**
- `llm/` - LLM providers (OpenAI, Ollama, etc.)
- `prompts/` - Prompt builders (RAG, conversational)
- `reranker/` - Re-ranking strategies

## Data Flows

### Ingestion Flow

```
1. User uploads document via Django
   ↓
2. Django saves metadata to DB
   ↓
3. Django triggers Ingest Service (HTTP POST)
   ↓
4. Ingest Service:
   a. Loads document (PDF/TXT/DOCX)
   b. Chunks text semantically
   c. Generates embeddings (OpenAI)
   d. Stores in Qdrant with tenant_id
   ↓
5. Callback to Django (update status)
```

### Query Flow

```
1. User sends query via Query API
   ↓
2. Query API:
   a. Generates query embedding
   b. Searches Qdrant (filtered by tenant_id)
   c. Re-ranks results
   d. Builds RAG prompt
   e. Calls LLM (OpenAI)
   ↓
3. Returns answer + sources to user
```

## Multi-Tenancy

### Implementation

- **Identifier:** `tenant_id` (mapped to Django's `user.id`)
- **Isolation:**
  - All documents have `tenant_id` in payload
  - All queries filter by `tenant_id`
  - Qdrant indices for performance

### Guarantees

```python
# ✅ Always filter by tenant_id
search(query_embedding, tenant_id=user.id)

# ❌ NEVER search without filter
search(query_embedding)  # Data leak!
```

## Security

### Principles

1. **Authentication:** Django handles (JWT/Session)
2. **Authorization:** User can only access own documents
3. **Tenant Isolation:** Mandatory `tenant_id` filtering
4. **API Keys:** Environment variables, never hardcoded
5. **Input Validation:** Pydantic models everywhere

### Checklist

- [ ] All queries filter by `tenant_id`
- [ ] API keys in `.env`, not in code
- [ ] Input validation with Pydantic
- [ ] Rate limiting (future)
- [ ] Audit logging (future)

## Scalability

### Current (MVP)

- Single instance of each service
- SQLite for Django (dev)
- Background tasks in FastAPI

### Future (Production)

- **Horizontal Scaling:**
  - Multiple Ingest workers
  - Multiple Query API instances
  - Load balancer (Nginx)

- **Task Queue:**
  - Celery + Redis for ingestion
  - Worker pools

- **Database:**
  - PostgreSQL for Django
  - Qdrant cluster

- **Monitoring:**
  - Prometheus + Grafana
  - Sentry for error tracking
  - Token usage tracking

## Observability

### Logging

All services use Python `logging`:

```python
logger.info(f"Document {doc_id} ingested for tenant {tenant_id}")
logger.error(f"Failed to process query: {e}", exc_info=True)
```

**Levels:**
- `DEBUG` - Internal details
- `INFO` - Important events
- `WARNING` - Non-critical issues
- `ERROR` - Errors requiring attention

### Metrics (Future)

- Token usage per tenant
- Query latency
- Success/failure rate
- Document sizes

## Architectural Principles

### SOLID

- **Single Responsibility:** Each module has one responsibility
- **Open/Closed:** Extensible via interfaces
- **Liskov Substitution:** Interchangeable LLM providers
- **Interface Segregation:** Small, focused interfaces
- **Dependency Inversion:** Depend on abstractions, not implementations

### Clean Architecture

```
┌─────────────────────────────────────┐
│   Frameworks & Drivers              │
│   (Django, FastAPI, Qdrant)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Interface Adapters                │
│   (Controllers, Views, Serializers) │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Application Business Rules        │
│   (Use Cases, Services)             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Enterprise Business Rules         │
│   (Entities, Domain Logic - Core)   │
└─────────────────────────────────────┘
```

### Dependency Rule

> Dependencies point inward (Core is the center)

```
Django/FastAPI → Services → Core
     ✓              ✓         ✓
Core ← Services ← Django/FastAPI
     ✗              ✗         ✗
```

## Design Decisions

### Why FastAPI for Ingest/Query?

- ✅ Native async/await
- ✅ Pydantic for validation
- ✅ Auto-documentation (OpenAPI)
- ✅ Performance

### Why Django for Web Backend?

- ✅ Built-in admin interface
- ✅ Robust ORM
- ✅ Authentication/authorization
- ✅ Mature ecosystem

### Why separate Ingest and Query?

- ✅ Independent scaling
- ✅ Independent deployment
- ✅ Failure isolation
- ✅ SRP (Single Responsibility Principle)

### Why Qdrant?

- ✅ Open-source
- ✅ High performance
- ✅ Filter support (tenant_id)
- ✅ Easy deployment

## Architectural TODOs

- [ ] Implement task queue (Celery)
- [ ] Add cache (Redis)
- [ ] Rate limiting
- [ ] API Gateway
- [ ] Service mesh (Istio?)
- [ ] Monitoring (Prometheus)
- [ ] Distributed tracing (Jaeger)
- [ ] Event sourcing (future)

---

**Document complete. Contributions are welcome!**
