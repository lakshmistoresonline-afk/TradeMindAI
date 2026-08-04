#!/bin/bash

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    # Start dummy server to prevent Render timeout
    python3 -m http.server $PORT &
    python -m celery -A backend.workers.tasks.celery_app worker --loglevel=info -P solo
elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Starting Celery Beat..."
    # Start dummy server to prevent Render timeout
    python3 -m http.server $PORT &
    python -m celery -A backend.workers.tasks.celery_app beat --loglevel=info
else
    echo "Starting FastAPI API..."
    # API doesn't need dummy server (it uses the port itself)
    uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
fi
