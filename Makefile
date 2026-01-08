.PHONY: help test test-cov test-unit test-integration test-watch clean install lint format

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instalar dependências"
	@echo "  make test          - Executar todos os testes"
	@echo "  make test-cov      - Executar testes com cobertura"
	@echo "  make test-unit     - Executar apenas testes unitários"
	@echo "  make test-integration - Executar apenas testes de integração"
	@echo "  make test-watch    - Executar testes em modo watch"
	@echo "  make lint          - Executar linter"
	@echo "  make format        - Formatar código"
	@echo "  make clean         - Limpar arquivos temporários"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Subir serviços Docker"
	@echo "  make docker-down   - Parar serviços Docker"
	@echo "  make docker-test   - Executar testes no Docker"
	@echo "  make docker-logs   - Ver logs dos containers"

install:
	pip install -r requirements.txt

test:
	pytest

test-cov:
	pytest --cov --cov-report=term-missing --cov-report=html

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-watch:
	pytest-watch

lint:
	flake8 core/ ingest/ api/ web/ --max-line-length=120

format:
	black core/ ingest/ api/ web/
	isort core/ ingest/ api/ web/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-test:
	docker-compose run --rm ingest pytest

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-clean:
	docker-compose down -v
	docker system prune -f
