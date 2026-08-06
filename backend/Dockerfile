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
    && rm -rf /var/lib/apt/lists/*

# Install specific numerical stack versions first to prevent binary conflicts
RUN pip install --upgrade pip setuptools wheel
RUN pip install "numpy==1.26.4" "pandas==2.2.2" "numba==0.59.1" "tqdm" "scikit-learn==1.5.0"

# Install remaining dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install pandas-ta without triggering dependency resolution for numpy/pandas
RUN pip install pandas-ta --no-deps

# Copy application code
# Since dockerContext is 'backend' in render.yaml, this copies everything in the backend folder
COPY . backend/

# Ensure start script is executable
RUN chmod +x backend/start.sh

# Run using the start script
CMD ["backend/start.sh"]
