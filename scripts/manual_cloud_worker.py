import os
import sys
import asyncio
import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. LOAD CLOUD ENV
# This points the script to your Neon Postgres and Cloud Firestore
load_dotenv(os.path.join("backend", ".env"))

from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic
from scripts.audit_database import ALL_SUPPORTED

async def run_manual_worker():
    print("\n--- TRADEMIND AI: 🚀 MANUAL CLOUD WORKER ENGINE ---")
    cloud_url = os.getenv('POSTGRES_URL')
    print(f"[*] Targeting Production Database: {cloud_url[:35]}...")
    print(f"[*] Universe: {len(ALL_SUPPORTED)} Stocks")

    for i, symbol in enumerate(ALL_SUPPORTED):
        print(f"[{i+1}/{len(ALL_SUPPORTED)}] Processing {symbol}...")
        try:
            # STEP A: Sync Data & Technicals
            # Logic: Price -> Indicators -> SMC -> Wyckoff -> Quant Metrics
            await _sync_stock_data_logic(symbol, period="1y")

            # STEP B: Run AI Analysis
            # Logic: Multi-Agent Consensus -> LiveSignal Generation
            result = await _analyze_stock_ai_logic(symbol)
            print(f"   [+] Result: {result}")

        except Exception as e:
            print(f"   [!] Pipeline Error for {symbol}: {e}")

        # Protective delay to prevent API throttling
        await asyncio.sleep(0.5)

    print("\n--- MANUAL WORKER FINISHED: Cloud Environment is Synchronized. ---")

if __name__ == "__main__":
    asyncio.run(run_manual_worker())
