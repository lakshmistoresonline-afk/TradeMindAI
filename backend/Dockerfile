FROM python:3.12-slim

# Set environment variables for non-interactive installs and memory safety
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install specific numerical stack versions
RUN pip install --upgrade pip setuptools wheel
RUN pip install "numpy==1.26.4" "pandas==2.2.2" "numba==0.59.1" "tqdm" "scikit-learn==1.5.0" "psycopg2-binary==2.9.12"

# Copy requirements - handle both root and backend contexts
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Install pandas-ta
RUN pip install pandas-ta --no-deps

# Copy source code
# We want the files to end up in /app/backend/ to support 'from backend...' imports
COPY . ./backend/

# Ensure start script is executable
RUN chmod +x backend/start.sh

# Run using the start script
CMD ["backend/start.sh"]
