#!/bin/bash

# TRADEMIND AI: AUTOMATED AWS WORKER SETUP SCRIPT
# This script installs Docker, clones the repo, configures the ENV, and launches the engine.

echo "--- TRADEMIND AI: INITIATING ENGINE ROOM SETUP ---"

# 1. System Update & Docker Installation
echo "[*] Installing Docker & Dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose git -y
sudo usermod -aG docker $USER

# 2. Repository Cloning
echo "[*] Cloning TradeMind AI Repository..."
git clone https://github.com/lakshmistoresonline-afk/TradeMindAI.git
cd TradeMindAI

# 3. Environment Configuration (Populated from Local Session)
echo "[*] Configuring Production Environment..."
mkdir -p backend
cat <<EOF > backend/.env
PROJECT_NAME="TradeMind AI"
REDIS_URL="redis://redis:6379/0"
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

FIREBASE_PROJECT_ID="com-webcraft-trademindai-c8f75"
FIREBASE_API_KEY="your-firebase-api-key"
POSTGRES_URL="postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
GROQ_API_KEY="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"

MARKET_DATA_PROVIDER="groww"
EOF

# 4. Launching Workers
echo "[*] Launching TradeMind Workers via Docker..."
sudo docker-compose -f docker-compose.workers.yml up --build -d

echo "--- SETUP COMPLETE ---"
echo "[!] Please LOG OUT and LOG BACK IN to enable Docker without sudo."
echo "[?] Monitor logs with: docker logs -f trademindai-worker-1"
