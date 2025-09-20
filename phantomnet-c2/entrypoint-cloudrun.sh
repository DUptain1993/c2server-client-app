#!/bin/bash
set -e

echo "Running database initialization..."
python /app/init_db.py

echo "Starting Gunicorn server for Cloud Run (HTTP only)..."
# Cloud Run handles SSL termination, so we run HTTP internally
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 4 --timeout 120 \
    phantomnet.app:app