# ==============================================================================
# TradeMindAI Hardened Multi-Stage Dockerfile (TM-01 & TM-10)
# ==============================================================================

FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --prefix=/install \
       "numpy==1.26.4" \
       "pandas==2.2.2" \
       "numba==0.59.1" \
       "scikit-learn==1.5.0" \
       "psycopg2-binary==2.9.12" \
    && python -m pip install --prefix=/install \
       -r requirements.txt \
    && python -m pip install --prefix=/install \
       --no-deps pandas-ta


FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app \
       --home-dir /app --no-create-home app

COPY --from=builder /install /usr/local

COPY backend/ /app/backend/
COPY scripts/ /app/scripts/
COPY docs/ /app/docs/
COPY alembic.ini /app/alembic.ini

RUN chmod 0555 /app/backend/start.sh \
    && chown -R root:root /app \
    && find /app -type d -exec chmod 0555 {} \; \
    && find /app -type f -exec chmod 0444 {} \; \
    && chmod 0555 /app/backend/start.sh

USER app:app

EXPOSE 8000

STOPSIGNAL SIGTERM

CMD ["bash", "/app/backend/start.sh"]
