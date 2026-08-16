import os
import sys
import asyncio
import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. Force Local LLM Mode before importing backend modules
os.environ["USE_LOCAL_LLM"] = "True"
# Ensure OLLAMA Model is set (llama3.1:8b is standard for local speed)
if not os.getenv("OLLAMA_MODEL"):
    os.environ["OLLAMA_MODEL"] = "llama3.1:8b"

# Load environment
load_dotenv(os.path.join("backend", ".env"))

from backend.core.config import settings
from backend.core.container import container
from scripts.audit_database import ALL_SUPPORTED
from backend.workers.tasks import _sync_stock_data_logic, _analyze_stock_ai_logic

async def populate_with_ollama():
    print("--- TRADEMIND AI: LOCAL OLLAMA POPULATION ENGINE ---")
    print(f"Model: {settings.OLLAMA_MODEL} | Base: {settings.OLLAMA_BASE_URL}")
    print(f"Targeting {len(ALL_SUPPORTED)} stocks...")

    for symbol in ALL_SUPPORTED:
        try:
            print(f"[*] Processing {symbol} via Local Alpha Agent...")

            # A. Sync 1Y History and Technicals
            # We use 1Y instead of 10Y for local speed unless full fidelity is needed
            await _sync_stock_data_logic(symbol, period="1y")

            # B. Run Local AI Consensus (Llama 3.1 8B)
            # This generates the LiveSignal and Structured Consensus
            result = await _analyze_stock_ai_logic(symbol)
            print(f"   [+] {symbol}: {result}")

        except Exception as e:
            print(f"   [!] Error processing {symbol}: {e}")

        # Local Ollama doesn't have rate limits, but we keep a small gap for CPU/GPU cooling
        await asyncio.sleep(0.5)

    print("--- OLLAMA POPULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(populate_with_ollama())
