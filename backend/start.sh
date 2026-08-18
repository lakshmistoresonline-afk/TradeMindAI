#!/bin/bash

# Ensure the app can find the backend package
export PYTHONPATH=$PYTHONPATH:/app

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    # Render fallback: Start dummy server if PORT is provided
    if [ -n "$PORT" ]; then python3 -m http.server $PORT & fi

    # Use prefork pool for VPS, solo for limited memory environments
    POOL_TYPE=${CELERY_POOL:-prefork}
    CONCURRENCY=${CELERY_CONCURRENCY:-2}

    python -m celery -A backend.workers.tasks.celery_app worker --loglevel=info -P $POOL_TYPE --concurrency=$CONCURRENCY
elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Starting Celery Beat..."
    if [ -n "$PORT" ]; then python3 -m http.server $PORT & fi
    python -m celery -A backend.workers.tasks.celery_app beat --loglevel=info
elif [ "$SERVICE_TYPE" = "shadow-worker" ]; then
    echo "Starting Shadow Celery Worker..."
    # Shadow worker strictly serial (concurrency=1)
    python -m celery -A backend.workers.tasks.celery_app worker --loglevel=info -Q shadow -P solo --concurrency=1
elif [ "$SERVICE_TYPE" = "shadow-beat" ]; then
    echo "Starting Shadow Celery Beat..."
    python -m celery -A backend.workers.tasks.celery_app beat --loglevel=info
else
    echo "Starting FastAPI API..."
    PORT=${PORT:-8000}
    uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers ${UVICORN_WORKERS:-1} --timeout-keep-alive 60
fi
