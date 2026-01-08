# Tests - Contexta

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_core/              # Core tests
│   ├── test_llm.py
│   ├── test_prompts.py
│   └── test_reranker.py
├── test_ingest/            # Ingest service tests
│   ├── test_chunking.py
│   ├── test_loaders.py
│   ├── test_embeddings.py
│   └── test_vectorstore.py
└── test_api/               # API tests
    └── test_main.py
```

## Running Tests

### All tests
```bash
pytest
```

### With coverage
```bash
pytest --cov
```

### Specific tests
```bash
# By module
pytest tests/test_core/

# By file
pytest tests/test_core/test_llm.py

# By class
pytest tests/test_core/test_llm.py::TestOpenAILLM

# By function
pytest tests/test_core/test_llm.py::TestOpenAILLM::test_generate
```

### With verbosity
```bash
pytest -v
pytest -vv  # More verbose
```

### Stop on first error
```bash
pytest -x
```

### Show print statements
```bash
pytest -s
```

## Running in Docker

### Run tests in container
```bash
docker-compose run --rm ingest pytest

# Or create a specific test service
docker-compose run --rm -e PYTHONPATH=/app test pytest
```

### Add to docker-compose.yml (optional)
```yaml
test:
  build: .
  command: pytest
  volumes:
    - .:/app
  environment:
    - OPENAI_API_KEY=test_key
    - QDRANT_URL=http://qdrant:6333
```

Then run:
```bash
docker-compose run --rm test
```

## Coverage

### Generate HTML report
```bash
pytest --cov --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Generate XML report (for CI/CD)
```bash
pytest --cov --cov-report=xml
```

## Available Fixtures

See `tests/conftest.py` for shared fixtures:

- `mock_openai_client`: Mock OpenAI client
- `mock_qdrant_client`: Mock Qdrant client
- `sample_text`: Sample text
- `sample_chunks`: Sample chunks
- `sample_embeddings`: Sample embeddings
- `sample_search_results`: Sample search results

## Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## CI/CD

### GitHub Actions (example)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          QDRANT_URL: http://localhost:6333
        run: |
          pytest --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

1. **Always use mocks** for external APIs (OpenAI, Qdrant)
2. **Test edge cases**: empty, None, large values
3. **Test errors**: verify exceptions are raised correctly
4. **Keep tests fast**: use mocks instead of real services
5. **One assert per test** (when possible)
6. **Descriptive names**: `test_generate_with_invalid_api_key`
7. **Organize in classes**: group related tests

## Example Complete Test

```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    """Tests for my feature."""
    
    @pytest.fixture
    def my_fixture(self):
        """Setup for tests."""
        return {"key": "value"}
    
    def test_basic_functionality(self, my_fixture):
        """Test basic case."""
        result = my_function(my_fixture)
        assert result == expected_value
    
    def test_error_handling(self):
        """Test error case."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
    
    @patch('module.external_api')
    def test_with_mock(self, mock_api):
        """Test with mocked external dependency."""
        mock_api.return_value = "mocked"
        result = my_function()
        assert result == "expected"
        mock_api.assert_called_once()
```

## Troubleshooting

### Import errors
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Tests too slow
- Use mocks for external APIs
- Mark slow tests with `@pytest.mark.slow`
- Run slow tests separately

### Low coverage
```bash
# See which lines aren't covered
pytest --cov --cov-report=term-missing
```

## Next Steps

- [ ] Add end-to-end integration tests
- [ ] Configure CI/CD on GitHub Actions
- [ ] Increase coverage to >90%
- [ ] Add performance tests
- [ ] Add load tests (stress tests)

---

**For more detailed testing guide, see [TESTING_GUIDE.md](TESTING_GUIDE.md)**
