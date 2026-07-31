#!/bin/bash
echo "Starting Nodus AI Backend..."

# Run ingest in background if ChromaDB missing
if [ ! -d "chroma_db" ]; then
    echo "ChromaDB not found — running ingest in background..."
    python scripts/ingest.py &
fi

# Start server immediately so Render detects the port
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}