#!/bin/bash
set -e

# Wait for Qdrant to be ready
echo "Waiting for Qdrant..."
until curl -f http://qdrant:6333/health > /dev/null 2>&1; do
  echo "Qdrant is unavailable - sleeping"
  sleep 2
done

echo "Qdrant is up - executing command"
exec "$@"

