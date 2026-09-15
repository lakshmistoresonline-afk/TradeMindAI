import asyncio
import datetime
import sys
import os
from dotenv import load_dotenv

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService

async def run_scan():
    print(f"=== Starting Targeted PRODUCTION Scan (Neon: {os.getenv('POSTGRES_URL')[:50]}...) ===")
    symbols = ["TCS", "RELIANCE", "INFY", "HDFCBANK", "ICICIBANK"]
    horizons = ["SHORT", "SWING", "LONG"]

    count = 0
    for h in horizons:
        for s in symbols:
            try:
                print(f"   Scanning {s} ({h})...")
                signal = await SignalEngine.generate_signal(s, asset_class="EQUITY", timeframe=h)
                if signal:
                    await SignalLedgerService.create_signal(signal)
                    print(f"   [+] {s} ({h}) SIGNAL CREATED.")
                    count += 1
            except Exception as e:
                print(f"   [!] {s} ({h}) ERROR: {e}")

    print(f"Scan Completed. Signals Generated: {count}")

if __name__ == "__main__":
    asyncio.run(run_scan())
