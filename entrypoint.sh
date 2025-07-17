#!/bin/bash
if [ "$1" = "serve" ]; then
    echo "🔥 Starting FastAPI server with Uvicorn..."
    exec python serve.py
else
    echo "🔁 Running passed command: $@"
    exec "$@"
fi