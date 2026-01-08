# Testes - Contexta

## Estrutura de Testes

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_core/              # Testes do core
│   ├── test_llm.py
│   ├── test_prompts.py
│   └── test_reranker.py
├── test_ingest/            # Testes do ingest
│   ├── test_chunking.py
│   ├── test_loaders.py
│   ├── test_embeddings.py
│   └── test_vectorstore.py
└── test_api/               # Testes da API
    └── test_main.py
```

## Executar Testes

### Todos os testes
```bash
pytest
```

### Com cobertura
```bash
pytest --cov
```

### Testes específicos
```bash
# Por módulo
pytest tests/test_core/

# Por arquivo
pytest tests/test_core/test_llm.py

# Por classe
pytest tests/test_core/test_llm.py::TestOpenAILLM

# Por função
pytest tests/test_core/test_llm.py::TestOpenAILLM::test_generate
```

### Com verbosidade
```bash
pytest -v
pytest -vv  # Mais verbose
```

### Parar no primeiro erro
```bash
pytest -x
```

### Ver print statements
```bash
pytest -s
```

## Executar no Docker

### Rodar testes em container
```bash
docker-compose run --rm ingest pytest

# Ou criar serviço específico de testes
docker-compose run --rm -e PYTHONPATH=/app test pytest
```

### Adicionar ao docker-compose.yml (opcional)
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

Depois rodar:
```bash
docker-compose run --rm test
```

## Cobertura

### Gerar relatório HTML
```bash
pytest --cov --cov-report=html
```

Depois abra `htmlcov/index.html` no navegador.

### Gerar relatório XML (para CI/CD)
```bash
pytest --cov --cov-report=xml
```

## Fixtures Disponíveis

Veja `tests/conftest.py` para fixtures compartilhadas:

- `mock_openai_client`: Mock do cliente OpenAI
- `mock_qdrant_client`: Mock do cliente Qdrant
- `sample_text`: Texto de exemplo
- `sample_chunks`: Chunks de exemplo
- `sample_embeddings`: Embeddings de exemplo
- `sample_search_results`: Resultados de busca de exemplo

## Markers

```bash
# Rodar apenas testes unitários
pytest -m unit

# Rodar apenas testes de integração
pytest -m integration

# Pular testes lentos
pytest -m "not slow"
```

## CI/CD

### GitHub Actions (exemplo)

Crie `.github/workflows/tests.yml`:

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
          python-version: '3.11'
      
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

## Boas Práticas

1. **Sempre use mocks** para APIs externas (OpenAI, Qdrant)
2. **Teste casos extremos**: vazio, None, valores grandes
3. **Teste erros**: verifique que exceções são lançadas corretamente
4. **Mantenha testes rápidos**: use mocks ao invés de serviços reais
5. **Um assert por teste** (quando possível)
6. **Nomes descritivos**: `test_generate_with_invalid_api_key`
7. **Organize em classes**: agrupe testes relacionados

## Exemplo de Teste Completo

```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    \"\"\"Tests for my feature.\"\"\"
    
    @pytest.fixture
    def my_fixture(self):
        \"\"\"Setup for tests.\"\"\"
        return {"key": "value"}
    
    def test_basic_functionality(self, my_fixture):
        \"\"\"Test basic case.\"\"\"
        result = my_function(my_fixture)
        assert result == expected_value
    
    def test_error_handling(self):
        \"\"\"Test error case.\"\"\"
        with pytest.raises(ValueError):
            my_function(invalid_input)
    
    @patch('module.external_api')
    def test_with_mock(self, mock_api):
        \"\"\"Test with mocked external dependency.\"\"\"
        mock_api.return_value = "mocked"
        result = my_function()
        assert result == "expected"
        mock_api.assert_called_once()
```

## Troubleshooting

### Import errors
```bash
# Adicionar ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Testes muito lentos
- Use mocks para APIs externas
- Marque testes lentos com `@pytest.mark.slow`
- Execute testes lentos separadamente

### Cobertura baixa
```bash
# Ver quais linhas não foram cobertas
pytest --cov --cov-report=term-missing
```

## Próximos Passos

- [ ] Adicionar testes de integração end-to-end
- [ ] Configurar CI/CD no GitHub Actions
- [ ] Aumentar cobertura para >90%
- [ ] Adicionar testes de performance
- [ ] Adicionar testes de carga (stress tests)

