# Makefile para facilitar comandos Docker

.PHONY: help build up down logs shell migrate createsuperuser clean restart

help:
	@echo "Comandos disponíveis:"
	@echo "  make build          - Reconstrói as imagens Docker"
	@echo "  make up             - Inicia todos os serviços"
	@echo "  make down           - Para todos os serviços"
	@echo "  make logs           - Mostra logs de todos os serviços"
	@echo "  make shell          - Abre shell no container Django"
	@echo "  make migrate        - Executa migrações do Django"
	@echo "  make createsuperuser - Cria superusuário do Django"
	@echo "  make clean          - Remove containers e volumes"
	@echo "  make restart        - Reinicia todos os serviços"
	@echo "  make test           - Executa testes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Serviços iniciados!"
	@echo "Django Admin: http://localhost:8000/admin"
	@echo "Query API: http://localhost:8002"
	@echo "Ingest Service: http://localhost:8001"
	@echo "Qdrant: http://localhost:6333/dashboard"

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec django python web/manage.py shell

migrate:
	docker-compose exec django python web/manage.py migrate

makemigrations:
	docker-compose exec django python web/manage.py makemigrations

createsuperuser:
	docker-compose exec django python web/manage.py createsuperuser

clean:
	docker-compose down -v
	@echo "Todos os containers e volumes foram removidos"

restart:
	docker-compose restart

test:
	docker-compose exec django python web/manage.py test

# Comandos de desenvolvimento
dev-django:
	docker-compose logs -f django

dev-ingest:
	docker-compose logs -f ingest

dev-api:
	docker-compose logs -f api

# Health checks
health:
	@echo "Verificando Qdrant..."
	@curl -s http://localhost:6333/health || echo "❌ Qdrant offline"
	@echo "\nVerificando Ingest Service..."
	@curl -s http://localhost:8001/health || echo "❌ Ingest offline"
	@echo "\nVerificando Query API..."
	@curl -s http://localhost:8002/health || echo "❌ API offline"
	@echo "\nVerificando Django..."
	@curl -s http://localhost:8000/admin/ > /dev/null && echo "✅ Django online" || echo "❌ Django offline"

