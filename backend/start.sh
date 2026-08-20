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
    echo "[+] Configuration Validated."
fi

# --- ZERO RAILWAY WORKER ENFORCEMENT (Phase 7.8 Correction) ---
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$SERVICE_TYPE" != "api" ]; then
        echo "[!] CRITICAL ERROR: RAILWAY_BACKGROUND_EXECUTION_DISABLED"
        echo "    Role '$SERVICE_TYPE' is forbidden in the cloud environment."
        echo "    Railway is reserved ONLY for API/Web serving."
        echo "    All heavy processing must run manually on local Windows infrastructure."
        exit 1
    fi
fi

# Note: Celery worker/beat branches removed to prevent accidental cloud execution.
# Background tasks are preserved in the codebase for local manual execution only.

echo "Starting FastAPI API..."
PORT=${PORT:-8000}
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers ${UVICORN_WORKERS:-1} --timeout-keep-alive 60
