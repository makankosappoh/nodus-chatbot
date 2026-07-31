#!/bin/bash
echo "Starting Nodus AI Backend..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}