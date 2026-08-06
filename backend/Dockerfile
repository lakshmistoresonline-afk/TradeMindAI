FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir "numpy==1.26.4" "pandas==2.2.2" "numba==0.59.1"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pandas-ta --no-deps

COPY . backend/

RUN chmod +x backend/start.sh

CMD ["backend/start.sh"]
