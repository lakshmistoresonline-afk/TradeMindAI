#!/bin/bash

# Start the dummy web server in the background for all services
# This prevents Render from timing out the "Web Service"
python3 -m http.server $PORT &

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    python -m celery -A backend.workers.tasks.celery_app worker --loglevel=info -P solo
elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Starting Celery Beat..."
    python -m celery -A backend.workers.tasks.celery_app beat --loglevel=info
else
    echo "Starting FastAPI API..."
    uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
fi
