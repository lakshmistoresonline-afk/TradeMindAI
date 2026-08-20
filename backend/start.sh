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

# --- EMERGENCY WORKER ELIMINATION (Phase 7.9) ---
if [ "$SERVICE_TYPE" != "api" ] && [ -n "$SERVICE_TYPE" ]; then
    echo "[!] CRITICAL ERROR: BACKGROUND WORKERS ARE DISABLED ON RAILWAY."
    echo "    Role '$SERVICE_TYPE' is not permitted in cloud environment."
    echo "    All background tasks must be executed manually from the local machine."
    exit 1
fi

echo "Starting FastAPI API..."
PORT=${PORT:-8000}
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers ${UVICORN_WORKERS:-1} --timeout-keep-alive 60
