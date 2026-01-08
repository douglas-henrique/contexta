# Running Contexta with Docker

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v2+
- OpenAI API key

## Quick Setup

### 1. Configure environment variables

```bash
# Copy the example file
cp .env.docker .env

# Edit .env and add your OPENAI_API_KEY
nano .env  # or vim, code, etc.
```

### 2. Run the entire project with a single command

```bash
docker-compose up
```

Or, to run in the background:

```bash
docker-compose up -d
```

## Available Services

After starting, you'll have access to:

- **Django Admin**: http://localhost:8000/admin
- **Django API**: http://localhost:8000/api/documents/
- **Ingest Service**: http://localhost:8001
- **Query API**: http://localhost:8002
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Useful Commands

### View logs from all services
```bash
docker-compose logs -f
```

### View logs from a specific service
```bash
docker-compose logs -f django
docker-compose logs -f ingest
docker-compose logs -f api
docker-compose logs -f qdrant
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes (clean everything)
```bash
docker-compose down -v
```

### Rebuild images
```bash
docker-compose build
docker-compose up
```

### Execute commands inside containers

```bash
# Django - create superuser
docker-compose exec django python web/manage.py createsuperuser

# Django - run migrations
docker-compose exec django python web/manage.py migrate

# Django - create migrations
docker-compose exec django python web/manage.py makemigrations

# Django - shell
docker-compose exec django python web/manage.py shell

# View Qdrant logs
docker-compose logs qdrant
```

## First Run

On the first run, you'll need to create a superuser:

```bash
# Start services
docker-compose up -d

# Wait a few seconds for services to start

# Create superuser
docker-compose exec django python web/manage.py createsuperuser

# Follow the instructions and create your user
```

## Testing the System

### 1. Access Django Admin
- URL: http://localhost:8000/admin
- Login with the created superuser

### 2. Upload a document
- In admin, go to "Documents"
- Click "Add Document"
- Upload a PDF
- The document will be automatically processed by the Ingest Service

### 3. Query documents
```bash
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "tenant_id": 1,
    "top_k": 10,
    "rerank_top_k": 5
  }'
```

## Health Checks

Check if all services are healthy:

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

## Development

For development with hot-reload:

```bash
# Volumes are mapped, so code changes
# are automatically reflected (hot-reload active)

docker-compose up
```

## Troubleshooting

### Service doesn't start
```bash
# View logs
docker-compose logs <service-name>

# Rebuild the image
docker-compose build <service-name>
docker-compose up <service-name>
```

### Corrupted database
```bash
# Remove Django volume
docker-compose down -v
docker-compose up
```

### Qdrant doesn't start
```bash
# Remove Qdrant volume
docker-compose down
docker volume rm contexta_qdrant_storage
docker-compose up
```

### Permission error
```bash
# On Linux, you may need to adjust permissions
sudo chown -R $USER:$USER .
```

## Environment Variables

All variables are in `.env`:

- `OPENAI_API_KEY`: Your OpenAI key (required)
- `DJANGO_SECRET_KEY`: Django secret key
- `DEBUG`: True for development, False for production
- `QDRANT_COLLECTION`: Collection name in Qdrant
- `OPENAI_EMBEDDING_MODEL`: Embedding model (text-embedding-3-large)

## Production

For production, make the following changes:

1. Change `DEBUG=False` in `.env`
2. Generate a secure new `DJANGO_SECRET_KEY`
3. Configure production variables in `.env`
4. Use a production server (gunicorn) instead of runserver
5. Configure a PostgreSQL database
6. Configure a reverse proxy web server (nginx)

## Architecture

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

Docker Compose creates the following volumes:

- `qdrant_storage`: Stores Qdrant data
- `django_static`: Django static files
- `django_media`: File uploads

For backup:

```bash
docker run --rm -v contexta_qdrant_storage:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant_backup.tar.gz /data
```

## Makefile Commands

For convenience, you can use the Makefile:

```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Rebuild and restart
make restart

# Clean everything (remove volumes)
make clean
```

---

**For more detailed information, see the main [README.md](../README.md)**
