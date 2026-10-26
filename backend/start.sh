#!/usr/bin/env bash
set -Eeuo pipefail

export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}/app"
export SERVICE_TYPE="${SERVICE_TYPE:-api}"

log() {
    printf '%s %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

fail() {
    log "FATAL: $*"
    exit 1
}

if [[ "${ENVIRONMENT:-development}" == "production" ]]; then
    [[ "$SERVICE_TYPE" == "api" ]] \
        || fail "Only SERVICE_TYPE=api is permitted in production."

    [[ -n "${POSTGRES_URL:-}" ]] \
        || fail "POSTGRES_URL is required in production."

    [[ -n "${REDIS_URL:-}" ]] \
        || fail "REDIS_URL is required in production."

    [[ -n "${SECRET_KEY:-}" ]] \
        || fail "SECRET_KEY is required in production."

    [[ "${SECRET_KEY}" != "SECRET" ]] \
        || fail "The default signing secret is prohibited."

    [[ "${#SECRET_KEY}" -ge 32 ]] \
        || fail "SECRET_KEY must be at least 32 characters."

    [[ -n "${MARKET_DATA_INGEST_KEY:-}" ]] \
        || fail "MARKET_DATA_INGEST_KEY is required."

    [[ "${MARKET_DATA_INGEST_KEY}" != "LOCAL_ONLY_DEV_KEY" ]] \
        || fail "The development ingest key is prohibited."

    [[ "${#MARKET_DATA_INGEST_KEY}" -ge 32 ]] \
        || fail "MARKET_DATA_INGEST_KEY must be at least 32 characters."

    [[ "${POSTGRES_URL}" == postgresql://* \
        || "${POSTGRES_URL}" == postgresql+psycopg2://* ]] \
        || fail "Production POSTGRES_URL must use PostgreSQL."
fi

PORT="${PORT:-8000}"

[[ "$PORT" =~ ^[0-9]+$ ]] \
    || fail "PORT must be an integer."

(( PORT >= 1 && PORT <= 65535 )) \
    || fail "PORT must be between 1 and 65535."

log "Starting TradeMindAI API on port ${PORT}."

exec python -m uvicorn backend.app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 1 \
    --timeout-keep-alive 15 \
    --timeout-graceful-shutdown 25
