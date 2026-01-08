# 🧪 Guia Completo de Testes - Contexta

## 📊 Visão Geral

Suíte completa de testes unitários para garantir qualidade e confiabilidade do código.

### Estatísticas
- **Total de Arquivos de Teste**: 12
- **Módulos Cobertos**: Core, Ingest, API
- **Tipos de Teste**: Unitários, Integração (CI/CD ready)
- **Framework**: pytest + pytest-cov + pytest-mock

---

## 🗂️ Estrutura de Testes

```
tests/
├── conftest.py                    # 🔧 Fixtures compartilhadas
│   ├── mock_openai_client         # Mock do OpenAI
│   ├── mock_qdrant_client         # Mock do Qdrant
│   ├── sample_text                # Textos de exemplo
│   ├── sample_chunks               # Chunks de exemplo
│   ├── sample_embeddings          # Embeddings de exemplo
│   └── sample_search_results      # Resultados de busca
│
├── test_core/                     # ✅ Testes do Core (Framework-agnostic)
│   ├── test_llm.py                # Testes de LLM providers
│   │   ├── TestOpenAILLM
│   │   │   ├── test_initialization
│   │   │   ├── test_generate
│   │   │   ├── test_generate_with_parameters
│   │   │   └── test_generate_stream
│   │   
│   ├── test_prompts.py            # Testes de Prompt Builders
│   │   └── TestRAGPromptBuilder
│   │       ├── test_initialization
│   │       ├── test_build_basic
│   │       ├── test_build_with_max_length
│   │       └── test_build_with_sources
│   │
│   └── test_reranker.py           # Testes de Re-rankers
│       └── TestSimpleReranker
│           ├── test_rerank_by_score
│           ├── test_rerank_top_k
│           └── test_rerank_empty_results
│
├── test_ingest/                   # 📥 Testes do Ingest Service
│   ├── test_chunking.py           # Testes de Chunking
│   │   └── TestSemanticChunking
│   │       ├── test_basic_chunking
│   │       ├── test_chunk_size
│   │       ├── test_chunk_overlap
│   │       └── test_empty_text
│   │
│   ├── test_loaders.py            # Testes de Document Loaders
│   │   ├── TestPDFLoader
│   │   │   └── test_load_pdf
│   │   └── TestLoaderFactory
│   │       ├── test_get_loader_pdf
│   │       ├── test_load_document_pdf
│   │       └── test_load_document_txt
│   │
│   ├── test_embeddings.py         # Testes de Embeddings
│   │   └── TestOpenAIEmbeddings
│   │       ├── test_embed_texts
│   │       └── test_embed_texts_custom_model
│   │
│   └── test_vectorstore.py        # Testes de Vector Store
│       └── TestQdrantVectorStore
│           ├── test_ensure_collection_exists
│           ├── test_store_embeddings
│           ├── test_search
│           └── test_search_with_filters
│
└── test_api/                      # 🚀 Testes da API
    └── test_main.py               # Testes de Endpoints
        └── TestAPIEndpoints
            ├── test_root_endpoint
            ├── test_health_endpoint
            ├── test_query_endpoint
            ├── test_query_endpoint_no_results
            └── test_query_endpoint_validation
```

---

## 🚀 Como Executar

### Método 1: Script de Teste (Recomendado)

```bash
# Todos os testes
./run_tests.sh

# Testes com cobertura (gera relatório HTML)
./run_tests.sh cov

# Apenas testes unitários
./run_tests.sh unit

# Apenas testes de integração
./run_tests.sh integration

# Testes rápidos (exclui @pytest.mark.slow)
./run_tests.sh fast

# Modo watch (reexecuta ao salvar arquivos)
./run_tests.sh watch
```

### Método 2: Poetry Direto

```bash
# Todos os testes com verbosidade
poetry run pytest -v

# Com cobertura
poetry run pytest --cov --cov-report=term-missing

# Testes específicos
poetry run pytest tests/test_core/test_llm.py

# Uma classe específica
poetry run pytest tests/test_core/test_llm.py::TestOpenAILLM

# Um teste específico
poetry run pytest tests/test_core/test_llm.py::TestOpenAILLM::test_generate

# Parar no primeiro erro
poetry run pytest -x

# Ver outputs (print statements)
poetry run pytest -s

# Modo watch
poetry run pytest-watch
```

### Método 3: Makefile

```bash
# Todos os testes
make test

# Com cobertura
make test-cov

# Apenas unitários
make test-unit

# Apenas integração
make test-integration
```

### Método 4: Docker

```bash
# Executar testes no container
docker-compose run --rm ingest poetry run pytest

# Com cobertura
docker-compose run --rm ingest poetry run pytest --cov

# Usando make
make docker-test
```

---

## 📈 Cobertura de Código

### Gerar Relatório

```bash
# Terminal
poetry run pytest --cov --cov-report=term-missing

# HTML (abre no navegador)
poetry run pytest --cov --cov-report=html
open htmlcov/index.html

# XML (para CI/CD)
poetry run pytest --cov --cov-report=xml
```

### Meta de Cobertura

- **Core**: 90%+
- **Ingest**: 85%+
- **API**: 80%+
- **Overall**: 85%+

---

## 🎯 Tipos de Testes

### Testes Unitários (`@pytest.mark.unit`)

- Testam componentes isolados
- Usam mocks para dependências externas
- Rápidos de executar (<1s por teste)
- Não requerem serviços externos

**Exemplo:**
```python
@pytest.mark.unit
def test_generate(mock_openai_client):
    llm = OpenAILLM(api_key="test")
    result = llm.generate("Test prompt")
    assert result == "Generated text"
```

### Testes de Integração (`@pytest.mark.integration`)

- Testam interação entre componentes
- Podem usar serviços reais (Qdrant, etc.)
- Mais lentos
- Ideais para CI/CD pipeline

**Exemplo:**
```python
@pytest.mark.integration
def test_end_to_end_query():
    # Usa Qdrant real, OpenAI real
    response = client.post("/query", json={"query": "test"})
    assert response.status_code == 200
```

### Testes Lentos (`@pytest.mark.slow`)

- Testes que demoram >5s
- Geralmente testes de integração ou end-to-end
- Podem ser pulados em desenvolvimento rápido

```bash
# Pular testes lentos
poetry run pytest -m "not slow"
```

---

## 🔧 Fixtures Disponíveis

### Mock Clients

```python
def test_with_openai(mock_openai_client):
    """mock_openai_client já configurado com respostas fake"""
    pass

def test_with_qdrant(mock_qdrant_client):
    """mock_qdrant_client já configurado com resultados fake"""
    pass
```

### Sample Data

```python
def test_chunking(sample_text):
    """sample_text contém texto de exemplo"""
    chunks = semantic_chunk(sample_text)
    assert len(chunks) > 0

def test_embeddings(sample_chunks):
    """sample_chunks contém lista de chunks"""
    pass

def test_search(sample_search_results):
    """sample_search_results contém resultados de busca mock"""
    pass
```

---

## 🧩 Boas Práticas Implementadas

### 1. Arrange-Act-Assert (AAA)

```python
def test_example():
    # Arrange: setup
    llm = OpenAILLM(api_key="test")
    
    # Act: execute
    result = llm.generate("prompt")
    
    # Assert: verify
    assert result == "expected"
```

### 2. Descriptive Test Names

```python
# ✅ Bom
def test_generate_with_invalid_api_key_raises_error():
    pass

# ❌ Ruim
def test_generate_error():
    pass
```

### 3. One Assert Per Test (quando possível)

```python
# ✅ Bom
def test_response_has_answer():
    assert "answer" in response.json()

def test_response_has_sources():
    assert "sources" in response.json()

# ❌ Evitar múltiplos asserts não relacionados
def test_response():
    assert "answer" in response.json()
    assert "sources" in response.json()
    assert response.status_code == 200
```

### 4. Usar Mocks para APIs Externas

```python
# ✅ Sempre use mocks para OpenAI, Qdrant em testes unitários
@patch('ingest.embeddings.openai.OpenAI')
def test_embed_texts(mock_openai):
    # Teste rápido, sem custo de API
    pass

# ❌ Nunca faça chamadas reais em testes unitários
def test_embed_texts_real():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Isso é lento e custa dinheiro!
```

### 5. Organize em Classes

```python
class TestOpenAILLM:
    """Agrupa todos os testes relacionados ao OpenAILLM"""
    
    def test_initialization(self):
        pass
    
    def test_generate(self):
        pass
    
    def test_generate_stream(self):
        pass
```

---

## 🚨 Troubleshooting

### Import Errors

```bash
# Adicionar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
poetry run pytest
```

### Testes Falhando Localmente mas Passando no CI

- Verifique variáveis de ambiente (`.env` vs CI secrets)
- Verifique dependências (versões diferentes?)
- Verifique sistema operacional (paths, line endings)

### Mock não está funcionando

```python
# ❌ Ruim: mock no lugar errado
@patch('core.llm.openai.OpenAI')  # Importação original

# ✅ Bom: mock onde é usado
@patch('tests.test_core.test_llm.OpenAI')  # Onde o teste importa
```

### Testes muito lentos

- Use `-n auto` para paralelização: `pytest -n auto`
- Pule testes lentos: `pytest -m "not slow"`
- Verifique se está usando mocks corretamente

---

## 🔄 CI/CD

### GitHub Actions

Os testes rodam automaticamente em cada push/PR.

**Workflow**: `.github/workflows/tests.yml`

- ✅ Executa em Python 3.12
- ✅ Sobe Qdrant como service
- ✅ Executa todos os testes
- ✅ Gera relatório de cobertura
- ✅ Upload para Codecov (opcional)
- ✅ Linting (flake8, black, isort)

### Badges (adicione ao README.md)

```markdown
![Tests](https://github.com/seu-usuario/contexta/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/seu-usuario/contexta/branch/main/graph/badge.svg)](https://codecov.io/gh/seu-usuario/contexta)
```

---

## 📚 Recursos Adicionais

### Documentação Pytest

- [pytest docs](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

### Próximos Passos

- [ ] Adicionar testes end-to-end completos
- [ ] Adicionar testes de performance
- [ ] Adicionar testes de carga (locust, k6)
- [ ] Configurar Codecov para relatórios de cobertura
- [ ] Adicionar mutation testing (mutmut)
- [ ] Adicionar property-based testing (hypothesis)

---

## ✅ Checklist de Testes

Antes de fazer PR, garanta que:

- [ ] Todos os testes passam: `./run_tests.sh`
- [ ] Cobertura >85%: `./run_tests.sh cov`
- [ ] Linting ok: `make lint`
- [ ] Formatação ok: `make format`
- [ ] Novos testes foram adicionados para novas features
- [ ] Testes usam mocks apropriados
- [ ] Testes têm nomes descritivos
- [ ] Documentação atualizada se necessário

---

**🎉 Pronto! Agora você tem uma suíte de testes profissional para o Contexta!**

