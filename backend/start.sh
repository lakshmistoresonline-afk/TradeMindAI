#!/bin/bash

# Ensure the app can find the backend package
export PYTHONPATH=$PYTHONPATH:/app

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    # Start dummy server to prevent Render timeout
    python3 -m http.server $PORT &
    # Run in pool=solo to minimize memory usage on single-core instances
    python -m celery -A backend.workers.tasks.celery_app worker --loglevel=info -P solo --concurrency=1
elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Starting Celery Beat..."
    # Start dummy server to prevent Render timeout
    python3 -m http.server $PORT &
    python -m celery -A backend.workers.tasks.celery_app beat --loglevel=info
else
    echo "Starting FastAPI API..."
    # Optimize uvicorn for limited memory: single worker, no reload
    uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 60
fi
