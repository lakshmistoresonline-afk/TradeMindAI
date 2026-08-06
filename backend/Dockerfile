FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir "Cython>=3.0.0"
RUN pip install --no-cache-dir -r requirements.txt

COPY . backend/

RUN chmod +x backend/start.sh

CMD ["backend/start.sh"]
