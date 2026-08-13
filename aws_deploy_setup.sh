#!/bin/bash

# TRADEMIND AI: AUTOMATED AWS WORKER SETUP SCRIPT (Hardened with Firebase Auth)
# This script installs Docker, clones the repo, configures the ENV, and launches the engine.

echo "--- TRADEMIND AI: INITIATING ENGINE ROOM SETUP ---"

# 1. System Update & Docker Installation
echo "[*] Installing Docker & Dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose git -y
sudo usermod -aG docker $USER

# 2. Repository Cloning
echo "[*] Cloning TradeMind AI Repository..."
if [ -d "TradeMindAI" ]; then
    cd TradeMindAI
    git pull origin main
else
    git clone https://github.com/lakshmistoresonline-afk/TradeMindAI.git
    cd TradeMindAI
fi

# 3. Environment Configuration
echo "[*] Configuring Production Environment..."
mkdir -p backend

# Overwrite service-account.json using Python to avoid shell escaping issues
python3 -c "import json; creds={'type': 'service_account', 'project_id': 'com-webcraft-trademindai-c8f75', 'private_key_id': '5a2ecbcb1a6f713944795093f7201dafc81c31be', 'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDMKMZukPNOBEIV\ngg3+JOqjnnL1wyJP1BYtWpBNrDTCmovQiPJlx6mqdHao0NRtm6/1z/dIBJ2CmcfZ\nrXJwQd20qbTGCBq9vHFS0BiBOxIMq+EPmsdyBGeXL/pKNheuxCqN1D6Xh1FZyVFU\n+WtZF2LPlICwjLiSIzkKHE/HOVE2DxiQFr1mLekKTrChKiCU3sYL3UiprG//va0n\n6vXCyehLmfrmBh2sepyMR2HmowjpzH5/iQhitwi2i/U+3m3VHSoNLNRTMlQmZ5xp\n2zux81O2PxhUwkHAkkYHBxT5noQPnZt1tAihXB/2QChhKoReOVL8DYPVRK2gAyJ0\n3UW2AbSjAgMBAAECggEAA7r9ATkx0Ouf/3+cXNf015+GDzqNDnNcImEEwP6UCjhD\ntMBD2Zs/3Ob64hPKxePx36Z4qL642BGSRsZ2EFoLwIjXTkUIpA3k7jPyNq5LIqMj\nXiMgYNN2xxrv0lpRrXZVJrlJmYA1+tOEYm6aSQr12cAnZ9Jybu0o1if1RzkjZD7z\Aw/BSrbGevjNsU8fmzRrL3+LJXk44H9Ammo+0akrDEodQelLOulXrBT0DU0bWnFK\n8RNV0QNPpU8DDMUkXkDauSAF2GGNUFa7fFIFbJW3HvWX+KcZ6LN0Phpsb5H7xYT0\n+U1BfhtaxiUa+BJpoNqxlzEvYmXeMrljxx6taGUptQKBgQDqCgO4JsQCCGTtP7IU\nVXWgH9tfjGR9fx1h0ScQMIOnAmdL+Q7Ic6QTzaJTyXtKJEPj22YOAf+nmoVHe7Oc\nkDziGE8cO3fBpo5MG7MmBudUjw2MG3MlyliKaVnYhv4cVpXx0waITPrkv4dXBykt\nAWiKOAhWmJUDZOGv8ujXwOxdFQKBgQDfUQAGiXlAvd7upZjGKj3GRhDzep+g5iS1\ncbvUfThQlIUxHIVbziWdSJywbKWguaM+h9vQFQLqiyhFsuEIxFj21PXh6C9cVHEi\nVOOfiGKId/S+FqlPhld1zg/i+5GwMXIE3Rjcthv+ErncwDd9ySHsz9N08SsaBH3M\nnQHkRLNo1wKBgQCKz+vK0rtZFU9/ZFMkOlfs5FhCQMvtn3J27Q3FTXEYopVP+2Xo\QKal1EaeeZd1rzLRN/U9A7R13XGFp3ott2NVGuP5M9Bg/H/T5m4IdPnKLprzaeiP\nFogTeE8A3XhkqHqBFw/90eLRwEPuu2GRvw8ZRAi2DAP+Ily19lZieZv3zQKBgBdr\nbj5BQpcYkn2inkACBBJ8HKD8Nitwl17z+4fQTgydVs6MuCullepFyDD0Y/ZUIZuY\nMeRDn9erGmEc3l7GALJ6KQM1D2p2bJr2Hh0H95VqRx98TutJInj3UFE0otXAib2a\n1lWnP45ItndBLVCivE0SipGUDTogSHUh7iXbUplnAoGBALfGPbn5aokj2Nwco/SM\nfoaTOBp8AMdClPUJeWuDAwluzJIriZx2vsSWpH/A15csa//rGlcdPB90qv2rxAO7\nG1DNVSxoqp5FkKkqqQigGp0JK1edcLFwZGsuvB1O3iEQ6ZOoZxAV/bC/mE1FaOfZ\nvWSRmNIJ2Xhmne8sRIoQNOK6\n-----END PRIVATE KEY-----\n', 'client_email': 'firebase-adminsdk-fbsvc@com-webcraft-trademindai-c8f75.iam.gserviceaccount.com', 'client_id': '104590117655426687280', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token', 'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs', 'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40com-webcraft-trademindai-c8f75.iam.gserviceaccount.com', 'universe_domain': 'googleapis.com'}; json.dump(creds, open('backend/service-account.json', 'w'), indent=2)"

cat <<EOF > backend/.env
PROJECT_NAME="TradeMind AI"
REDIS_URL="redis://redis:6379/0"
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
FIREBASE_PROJECT_ID="com-webcraft-trademindai-c8f75"
POSTGRES_URL="postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
GROQ_API_KEY="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"
MARKET_DATA_PROVIDER="groww"
EOF

# 4. Launching Workers
echo "[*] Launching TradeMind Workers via Docker..."
sudo docker-compose -f docker-compose.workers.yml up --build -d

echo "--- SETUP RE-SYNCHRONIZED ---"
echo "[!] Monitor logs with: docker logs -f trademindai-worker-1"
