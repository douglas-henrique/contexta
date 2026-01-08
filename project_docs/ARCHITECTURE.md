# 🏗️ Arquitetura do Contexta

> **Status:** 🚧 Documento em construção

## Visão Geral

Contexta é uma aplicação RAG (Retrieval-Augmented Generation) SaaS construída com arquitetura limpa e separação rigorosa de responsabilidades.

## Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│                    [Separado - não implementado]                 │
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

## Componentes Principais

### 1. Django Web Backend (`web/`)

**Responsabilidades:**
- Autenticação e autorização de usuários
- Gerenciamento de multi-tenancy (tenant_id = user.id)
- CRUD de metadados de documentos
- Upload e armazenamento de arquivos
- Rastreamento de uso e billing
- Interface administrativa

**Tecnologias:**
- Django 6.x
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod)
- Django Admin

**Endpoints Principais:**
- `/admin/` - Interface administrativa
- `/api/documents/` - CRUD de documentos
- `/api/users/` - Gerenciamento de usuários

### 2. Ingest Service (`ingest/`)

**Responsabilidades:**
- Carregar documentos (PDF, TXT, DOCX)
- Chunking semântico de texto
- Geração de embeddings (OpenAI)
- Armazenamento em vector store (Qdrant)
- Processamento assíncrono em background

**Tecnologias:**
- FastAPI
- pypdf (PDF loading)
- OpenAI API (embeddings)
- Qdrant Client
- Background Tasks

**Endpoints:**
- `POST /ingest` - Trigger document ingestion
- `GET /health` - Health check

**Fluxo:**
```
Document Upload → Load → Chunk → Embed → Store in Qdrant
```

### 3. Query API Service (`api/`)

**Responsabilidades:**
- Receber queries de usuários
- Gerar embedding da query
- Buscar documentos similares (vector search)
- Re-rancar resultados
- Construir prompts com contexto
- Gerar respostas usando LLM

**Tecnologias:**
- FastAPI
- OpenAI API (chat completions)
- Qdrant Client

**Endpoints:**
- `POST /query` - Process RAG query
- `GET /health` - Health check

**Fluxo:**
```
User Query → Embed → Search → Rerank → Prompt → LLM → Response
```

### 4. Core Package (`core/`)

**Responsabilidades:**
- Abstrações de LLM (provider-agnostic)
- Builders de prompts
- Estratégias de re-ranking
- Lógica de domínio pura

**Princípios:**
- ✅ Framework-agnostic (sem Django, FastAPI)
- ✅ Testável isoladamente
- ✅ Dependency Injection
- ✅ Interfaces claras

**Módulos:**
- `llm/` - LLM providers (OpenAI, Ollama, etc.)
- `prompts/` - Prompt builders (RAG, conversational)
- `reranker/` - Re-ranking strategies

## Fluxo de Dados

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

### Implementação

- **Identificador:** `tenant_id` (mapeado para `user.id` do Django)
- **Isolamento:**
  - Todos os documentos têm `tenant_id` no payload
  - Todas as queries filtram por `tenant_id`
  - Índices no Qdrant para performance

### Garantias

```python
# ✅ Sempre filtrar por tenant_id
search(query_embedding, tenant_id=user.id)

# ❌ NUNCA buscar sem filtro
search(query_embedding)  # Vazamento de dados!
```

## Segurança

### Princípios

1. **Autenticação:** Django handles (JWT/Session)
2. **Autorização:** User can only access own documents
3. **Tenant Isolation:** Mandatory `tenant_id` filtering
4. **API Keys:** Environment variables, never hardcoded
5. **Input Validation:** Pydantic models everywhere

### Checklist

- [ ] Todas as queries filtram por `tenant_id`
- [ ] API keys em `.env`, não no código
- [ ] Input validation com Pydantic
- [ ] Rate limiting (futuro)
- [ ] Audit logging (futuro)

## Escalabilidade

### Atual (MVP)

- Single instance de cada serviço
- SQLite para Django (dev)
- Background tasks no FastAPI

### Futuro (Produção)

- **Horizontal Scaling:**
  - Multiple Ingest workers
  - Multiple Query API instances
  - Load balancer (Nginx)

- **Task Queue:**
  - Celery + Redis para ingestion
  - Worker pools

- **Database:**
  - PostgreSQL para Django
  - Qdrant cluster

- **Monitoring:**
  - Prometheus + Grafana
  - Sentry para error tracking
  - Token usage tracking

## Observabilidade

### Logging

Todos os serviços usam Python `logging`:

```python
logger.info(f"Document {doc_id} ingested for tenant {tenant_id}")
logger.error(f"Failed to process query: {e}", exc_info=True)
```

**Níveis:**
- `DEBUG` - Detalhes internos
- `INFO` - Eventos importantes
- `WARNING` - Problemas não críticos
- `ERROR` - Erros que requerem atenção

### Métricas (Futuro)

- Token usage por tenant
- Latência de queries
- Taxa de sucesso/falha
- Tamanho de documentos

## Princípios Arquiteturais

### SOLID

- **Single Responsibility:** Cada módulo tem uma responsabilidade
- **Open/Closed:** Extensível via interfaces
- **Liskov Substitution:** LLM providers intercambiáveis
- **Interface Segregation:** Interfaces pequenas e focadas
- **Dependency Inversion:** Dependa de abstrações, não implementações

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

> Dependências apontam para dentro (Core é o centro)

```
Django/FastAPI → Services → Core
     ✓              ✓         ✓
Core ← Services ← Django/FastAPI
     ✗              ✗         ✗
```

## Decisões de Design

### Por que FastAPI para Ingest/Query?

- ✅ Async/await nativo
- ✅ Pydantic para validação
- ✅ Auto-documentação (OpenAPI)
- ✅ Performance

### Por que Django para Web Backend?

- ✅ Admin interface built-in
- ✅ ORM robusto
- ✅ Autenticação/autorização
- ✅ Ecosystem maduro

### Por que separar Ingest e Query?

- ✅ Scaling independente
- ✅ Deploy independente
- ✅ Isolamento de falhas
- ✅ SRP (Single Responsibility)

### Por que Qdrant?

- ✅ Open-source
- ✅ Alta performance
- ✅ Suporte a filtros (tenant_id)
- ✅ Fácil deploy

## TODOs Arquiteturais

- [ ] Implementar task queue (Celery)
- [ ] Adicionar cache (Redis)
- [ ] Rate limiting
- [ ] API Gateway
- [ ] Service mesh (Istio?)
- [ ] Monitoring (Prometheus)
- [ ] Distributed tracing (Jaeger)
- [ ] Event sourcing (futuro)

---

**Documento em construção. Contribuições são bem-vindas!**

