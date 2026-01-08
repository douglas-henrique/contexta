# Rodando Contexta com Docker

## Pré-requisitos

- Docker Desktop instalado e rodando
- Docker Compose v2+
- OpenAI API key

## Setup Rápido

### 1. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.docker .env

# Edite o .env e adicione sua OPENAI_API_KEY
nano .env  # ou vim, code, etc.
```

### 2. Rode todo o projeto com um único comando

```bash
docker-compose up
```

Ou, para rodar em background:

```bash
docker-compose up -d
```

## Serviços Disponíveis

Após iniciar, você terá acesso a:

- **Django Admin**: http://localhost:8000/admin
- **Django API**: http://localhost:8000/api/documents/
- **Ingest Service**: http://localhost:8001
- **Query API**: http://localhost:8002
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Comandos Úteis

### Ver logs de todos os serviços
```bash
docker-compose logs -f
```

### Ver logs de um serviço específico
```bash
docker-compose logs -f django
docker-compose logs -f ingest
docker-compose logs -f api
docker-compose logs -f qdrant
```

### Parar todos os serviços
```bash
docker-compose down
```

### Parar e remover volumes (limpar tudo)
```bash
docker-compose down -v
```

### Reconstruir as imagens
```bash
docker-compose build
docker-compose up
```

### Executar comandos dentro dos containers

```bash
# Django - criar superusuário
docker-compose exec django python web/manage.py createsuperuser

# Django - executar migrações
docker-compose exec django python web/manage.py migrate

# Django - criar migrações
docker-compose exec django python web/manage.py makemigrations

# Django - shell
docker-compose exec django python web/manage.py shell

# Ver logs do Qdrant
docker-compose logs qdrant
```

## Primeira Execução

Na primeira vez que rodar, você precisará criar um superusuário:

```bash
# Inicie os serviços
docker-compose up -d

# Aguarde alguns segundos para os serviços iniciarem

# Crie o superusuário
docker-compose exec django python web/manage.py createsuperuser

# Siga as instruções e crie seu usuário
```

## Testando o Sistema

### 1. Acesse o Django Admin
- URL: http://localhost:8000/admin
- Login com o superusuário criado

### 2. Faça upload de um documento
- No admin, vá em "Documents"
- Clique em "Add Document"
- Faça upload de um PDF
- O documento será processado automaticamente pelo Ingest Service

### 3. Consulte os documentos
```bash
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual é o tema principal?",
    "tenant_id": 1,
    "top_k": 10,
    "rerank_top_k": 5
  }'
```

## Health Checks

Verifique se todos os serviços estão saudáveis:

```bash
# Qdrant
curl http://localhost:6333/health

# Django
curl http://localhost:8000/admin/

# Ingest Service
curl http://localhost:8001/health

# Query API
curl http://localhost:8002/health
```

## Desenvolvimento

Para desenvolvimento com hot-reload:

```bash
# Os volumes estão mapeados, então mudanças no código
# são refletidas automaticamente (hot-reload ativo)

docker-compose up
```

## Troubleshooting

### Serviço não inicia
```bash
# Veja os logs
docker-compose logs <nome-do-servico>

# Reconstrua a imagem
docker-compose build <nome-do-servico>
docker-compose up <nome-do-servico>
```

### Banco de dados corrompido
```bash
# Remova o volume do Django
docker-compose down -v
docker-compose up
```

### Qdrant não inicia
```bash
# Remova o volume do Qdrant
docker-compose down
docker volume rm contexta_qdrant_storage
docker-compose up
```

### Erro de permissão
```bash
# No Linux, pode ser necessário ajustar permissões
sudo chown -R $USER:$USER .
```

## Variáveis de Ambiente

Todas as variáveis estão no `.env`:

- `OPENAI_API_KEY`: Sua chave da OpenAI (obrigatório)
- `DJANGO_SECRET_KEY`: Chave secreta do Django
- `DEBUG`: True para desenvolvimento, False para produção
- `QDRANT_COLLECTION`: Nome da collection no Qdrant
- `OPENAI_EMBEDDING_MODEL`: Modelo de embedding (text-embedding-3-large)

## Produção

Para produção, faça as seguintes alterações:

1. Altere `DEBUG=False` no `.env`
2. Gere uma nova `DJANGO_SECRET_KEY` segura
3. Configure variáveis de produção no `.env`
4. Use um servidor de produção (gunicorn) ao invés do runserver
5. Configure um banco de dados PostgreSQL
6. Configure um servidor web reverso (nginx)

## Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Django    │────▶│    Ingest    │────▶│   Qdrant     │
│  (Port 8000)│     │  (Port 8001) │     │  (Port 6333) │
└─────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  │
                                           ┌──────▼───────┐
                                           │  Query API   │
                                           │  (Port 8002) │
                                           └──────────────┘
```

## Volumes

O Docker Compose cria os seguintes volumes:

- `qdrant_storage`: Armazena dados do Qdrant
- `django_static`: Arquivos estáticos do Django
- `django_media`: Uploads de arquivos

Para backup:

```bash
docker run --rm -v contexta_qdrant_storage:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant_backup.tar.gz /data
```

