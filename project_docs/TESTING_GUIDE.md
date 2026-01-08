# 🧪 Complete Testing Guide - Contexta

## 📊 Overview

Complete unit test suite to ensure code quality and reliability.

### Statistics
- **Total Test Files**: 12
- **Modules Covered**: Core, Ingest, API
- **Test Types**: Unit, Integration (CI/CD ready)
- **Framework**: pytest + pytest-cov + pytest-mock

---

## 🗂️ Test Structure

```
tests/
├── conftest.py                    # 🔧 Shared fixtures
│   ├── mock_openai_client         # OpenAI mock
│   ├── mock_qdrant_client         # Qdrant mock
│   ├── sample_text                # Sample texts
│   ├── sample_chunks               # Sample chunks
│   ├── sample_embeddings          # Sample embeddings
│   └── sample_search_results      # Sample search results
│
├── test_core/                     # ✅ Core Tests (Framework-agnostic)
│   ├── test_llm.py                # LLM provider tests
│   │   └── TestOpenAILLM
│   │       ├── test_initialization
│   │       ├── test_generate
│   │       ├── test_generate_with_parameters
│   │       └── test_generate_stream
│   │   
│   ├── test_prompts.py            # Prompt Builder tests
│   │   └── TestRAGPromptBuilder
│   │       ├── test_initialization
│   │       ├── test_build_basic
│   │       ├── test_build_with_max_length
│   │       └── test_build_with_sources
│   │
│   └── test_reranker.py           # Re-ranker tests
│       └── TestSimpleReranker
│           ├── test_rerank_by_score
│           ├── test_rerank_top_k
│           └── test_rerank_empty_results
│
├── test_ingest/                   # 📥 Ingest Service Tests
│   ├── test_chunking.py           # Chunking tests
│   │   └── TestSemanticChunking
│   │       ├── test_basic_chunking
│   │       ├── test_chunk_size
│   │       ├── test_chunk_overlap
│   │       └── test_empty_text
│   │
│   ├── test_loaders.py            # Document Loader tests
│   │   ├── TestPDFLoader
│   │   │   └── test_load_pdf
│   │   └── TestLoaderFactory
│   │       ├── test_get_loader_pdf
│   │       ├── test_load_document_pdf
│   │       └── test_load_document_txt
│   │
│   ├── test_embeddings.py         # Embedding tests
│   │   └── TestOpenAIEmbeddings
│   │       ├── test_embed_texts
│   │       └── test_embed_texts_custom_model
│   │
│   └── test_vectorstore.py        # Vector Store tests
│       └── TestQdrantVectorStore
│           ├── test_ensure_collection_exists
│           ├── test_store_embeddings
│           ├── test_search
│           └── test_search_with_filters
│
└── test_api/                      # 🚀 API Tests
    └── test_main.py               # Endpoint tests
        └── TestAPIEndpoints
            ├── test_root_endpoint
            ├── test_health_endpoint
            ├── test_query_endpoint
            ├── test_query_endpoint_no_results
            └── test_query_endpoint_validation
```

---

## 🚀 How to Run

### Method 1: Test Script (Recommended)

```bash
# All tests
./run_tests.sh

# Tests with coverage (generates HTML report)
./run_tests.sh cov

# Only unit tests
./run_tests.sh unit

# Only integration tests
./run_tests.sh integration

# Fast tests (excludes @pytest.mark.slow)
./run_tests.sh fast

# Watch mode (reruns on file save)
./run_tests.sh watch
```

### Method 2: Poetry Direct

```bash
# All tests with verbosity
poetry run pytest -v

# With coverage
poetry run pytest --cov --cov-report=term-missing

# Specific tests
poetry run pytest tests/test_core/test_llm.py

# A specific class
poetry run pytest tests/test_core/test_llm.py::TestOpenAILLM

# A specific test
poetry run pytest tests/test_core/test_llm.py::TestOpenAILLM::test_generate

# Stop on first error
poetry run pytest -x

# Show outputs (print statements)
poetry run pytest -s

# Watch mode
poetry run pytest-watch
```

### Method 3: Makefile

```bash
# All tests
make test

# With coverage
make test-cov

# Only unit tests
make test-unit

# Only integration tests
make test-integration
```

### Method 4: Docker

```bash
# Run tests in container
docker-compose run --rm ingest poetry run pytest

# With coverage
docker-compose run --rm ingest poetry run pytest --cov

# Using make
make docker-test
```

---

## 📈 Code Coverage

### Generate Report

```bash
# Terminal
poetry run pytest --cov --cov-report=term-missing

# HTML (opens in browser)
poetry run pytest --cov --cov-report=html
open htmlcov/index.html

# XML (for CI/CD)
poetry run pytest --cov --cov-report=xml
```

### Coverage Goals

- **Core**: 90%+
- **Ingest**: 85%+
- **API**: 80%+
- **Overall**: 85%+

---

## 🎯 Test Types

### Unit Tests (`@pytest.mark.unit`)

- Test isolated components
- Use mocks for external dependencies
- Fast to run (<1s per test)
- Don't require external services

**Example:**
```python
@pytest.mark.unit
def test_generate(mock_openai_client):
    llm = OpenAILLM(api_key="test")
    result = llm.generate("Test prompt")
    assert result == "Generated text"
```

### Integration Tests (`@pytest.mark.integration`)

- Test interaction between components
- May use real services (Qdrant, etc.)
- Slower
- Ideal for CI/CD pipeline

**Example:**
```python
@pytest.mark.integration
def test_end_to_end_query():
    # Uses real Qdrant, real OpenAI
    response = client.post("/query", json={"query": "test"})
    assert response.status_code == 200
```

### Slow Tests (`@pytest.mark.slow`)

- Tests that take >5s
- Usually integration or end-to-end tests
- Can be skipped during rapid development

```bash
# Skip slow tests
poetry run pytest -m "not slow"
```

---

## 🔧 Available Fixtures

### Mock Clients

```python
def test_with_openai(mock_openai_client):
    """mock_openai_client already configured with fake responses"""
    pass

def test_with_qdrant(mock_qdrant_client):
    """mock_qdrant_client already configured with fake results"""
    pass
```

### Sample Data

```python
def test_chunking(sample_text):
    """sample_text contains sample text"""
    chunks = semantic_chunk(sample_text)
    assert len(chunks) > 0

def test_embeddings(sample_chunks):
    """sample_chunks contains list of chunks"""
    pass

def test_search(sample_search_results):
    """sample_search_results contains mock search results"""
    pass
```

---

## 🧩 Best Practices Implemented

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
# ✅ Good
def test_generate_with_invalid_api_key_raises_error():
    pass

# ❌ Bad
def test_generate_error():
    pass
```

### 3. One Assert Per Test (when possible)

```python
# ✅ Good
def test_response_has_answer():
    assert "answer" in response.json()

def test_response_has_sources():
    assert "sources" in response.json()

# ❌ Avoid multiple unrelated asserts
def test_response():
    assert "answer" in response.json()
    assert "sources" in response.json()
    assert response.status_code == 200
```

### 4. Use Mocks for External APIs

```python
# ✅ Always use mocks for OpenAI, Qdrant in unit tests
@patch('ingest.embeddings.openai.OpenAI')
def test_embed_texts(mock_openai):
    # Fast test, no API cost
    pass

# ❌ Never make real calls in unit tests
def test_embed_texts_real():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # This is slow and costs money!
```

### 5. Organize in Classes

```python
class TestOpenAILLM:
    """Groups all tests related to OpenAILLM"""
    
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
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
poetry run pytest
```

### Tests Failing Locally but Passing in CI

- Check environment variables (`.env` vs CI secrets)
- Check dependencies (different versions?)
- Check operating system (paths, line endings)

### Mock Not Working

```python
# ❌ Bad: mock in wrong place
@patch('core.llm.openai.OpenAI')  # Original import

# ✅ Good: mock where it's used
@patch('tests.test_core.test_llm.OpenAI')  # Where test imports
```

### Tests Too Slow

- Use `-n auto` for parallelization: `pytest -n auto`
- Skip slow tests: `pytest -m "not slow"`
- Check if you're using mocks correctly

---

## 🔄 CI/CD

### GitHub Actions

Tests run automatically on each push/PR.

**Workflow**: `.github/workflows/tests.yml`

- ✅ Runs on Python 3.12
- ✅ Starts Qdrant as service
- ✅ Runs all tests
- ✅ Generates coverage report
- ✅ Upload to Codecov (optional)
- ✅ Linting (flake8, black, isort)

### Badges (add to README.md)

```markdown
![Tests](https://github.com/your-user/contexta/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/your-user/contexta/branch/main/graph/badge.svg)](https://codecov.io/gh/your-user/contexta)
```

---

## 📚 Additional Resources

### Pytest Documentation

- [pytest docs](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

### Next Steps

- [ ] Add complete end-to-end tests
- [ ] Add performance tests
- [ ] Add load tests (locust, k6)
- [ ] Configure Codecov for coverage reports
- [ ] Add mutation testing (mutmut)
- [ ] Add property-based testing (hypothesis)

---

## ✅ Testing Checklist

Before making a PR, ensure:

- [ ] All tests pass: `./run_tests.sh`
- [ ] Coverage >85%: `./run_tests.sh cov`
- [ ] Linting ok: `make lint`
- [ ] Formatting ok: `make format`
- [ ] New tests added for new features
- [ ] Tests use appropriate mocks
- [ ] Tests have descriptive names
- [ ] Documentation updated if necessary

---

**🎉 Ready! You now have a professional test suite for Contexta!**
