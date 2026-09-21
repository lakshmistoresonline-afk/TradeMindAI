#!/bin/bash

# Ensure the app can find the backend package
export PYTHONPATH=$PYTHONPATH:/app
export SERVICE_TYPE=${SERVICE_TYPE:-api}

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

# --- PRODUCTION SCHEMA MANAGEMENT (Phase 4 Hardening) ---
if [ "$ENVIRONMENT" = "production" ]; then
    echo "[*] AUDIT: Executing Alembic migrations..."
    echo "[*] DEBUG: Current Directory: $(pwd)"
    echo "[*] DEBUG: Files in Root: $(ls -F)"

    # Config is now at the root (/app/alembic.ini)
    if [ -f "/app/alembic.ini" ]; then
        alembic -c /app/alembic.ini upgrade head
        if [ $? -ne 0 ]; then
            echo "[!] CRITICAL ERROR: Alembic migration failed. Aborting startup."
            exit 1
        fi
    else
        echo "[!] CRITICAL ERROR: /app/alembic.ini NOT FOUND. Build integrity failure."
        exit 1
    fi
    echo "[+] Database schema synchronized."
fi

echo "Starting FastAPI API..."

PORT=${PORT:-8000}
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 60
