FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.128.0 \
    uvicorn>=0.40.0 \
    django>=6.0.1 \
    python-dotenv>=1.2.1 \
    pypdf>=5.0.0 \
    openai>=1.0.0 \
    qdrant-client>=1.7.0 \
    djangorestframework>=3.15.0 \
    djangorestframework-simplejwt>=5.3.1 \
    django-cors-headers>=4.6.0 \
    httpx>=0.27.0 \
    python-docx>=1.1.0

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8001 8002

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

