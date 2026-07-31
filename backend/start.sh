#!/bin/bash
echo "Starting Nodus AI Backend..."

# Rebuild ChromaDB if not present
if [ ! -d "chroma_db" ]; then
    echo "ChromaDB not found — running ingest..."
    python scripts/ingest.py
fi

# Start FastAPI on Render's required port
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}