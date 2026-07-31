#!/bin/bash
echo "Starting Nodus AI Backend..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}