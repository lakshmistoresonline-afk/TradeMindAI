#!/bin/bash

# Ensure the app can find the backend package
export PYTHONPATH=$PYTHONPATH:/app

echo "[*] BOOTSTRAP: Detected SERVICE_TYPE='$SERVICE_TYPE'"

# --- PRODUCTION CONFIGURATION VALIDATION (Phase 7.3) ---
if [ "$ENVIRONMENT" = "production" ]; then
    echo "--- PRODUCTION CONFIGURATION VALIDATION ---"
    if [ -z "$POSTGRES_URL" ]; then
        echo "[!] CRITICAL ERROR: POSTGRES_URL is missing in production environment."
        exit 1
    fi
    if [ -z "$REDIS_URL" ]; then
        echo "[!] CRITICAL ERROR: REDIS_URL is missing in production environment."
        exit 1
    fi
    echo "ENVIRONMENT: production"
    echo "DATABASE: PostgreSQL (Authoritative)"
    echo "SERVICE_TYPE: $SERVICE_TYPE"
    echo "[+] Configuration Validated. Starting Service..."
fi

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
    if [ -n "$PORT" ]; then python3 -m http.server $PORT & fi
    # Shadow worker strictly serial (concurrency=1)
    python -m celery -A backend.workers.tasks.celery_app worker --loglevel=info -Q shadow -P solo --concurrency=1
elif [ "$SERVICE_TYPE" = "shadow-beat" ]; then
    echo "Starting Shadow Celery Beat..."
    if [ -n "$PORT" ]; then python3 -m http.server $PORT & fi
    python -m celery -A backend.workers.tasks.celery_app beat --loglevel=info
else
    echo "Starting FastAPI API..."
    PORT=${PORT:-8000}
    uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers ${UVICORN_WORKERS:-1} --timeout-keep-alive 60
fi
