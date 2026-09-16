import os
import asyncio
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.core.container import container
from backend.services.price_resolver import PriceResolver
from backend.services.signal_ledger_service import SignalLedgerService

load_dotenv('backend/.env')

async def refresh():
    print("[*] Refreshing Active Signal Prices...")

    # 1. Fetch Active Signals
    active_signals = await container.ios_repo.get_active_live_signals()
    # Also fetch WAITING_FOR_ENTRY
    all_signals = await container.ios_repo.get_all_live_signals()
    non_terminal = [s for s in all_signals if s.status in ["WAITING_FOR_ENTRY", "ENTRY_TRIGGERED", "ACTIVE"]]

    print(f"   Found {len(non_terminal)} non-terminal signals.")

    for signal in non_terminal:
        print(f"   - Resolving for {signal.symbol}...")
        try:
            res = await PriceResolver.resolve_current_price(signal)
            if res["status"] == "FRESH":
                price = res["current_price"]
                updates = {
                    "current_price": price,
                    "current_price_timestamp": res["timestamp"],
                    "current_price_source": res["source"],
                    "current_price_status": "FRESH"
                }
                success = await SignalLedgerService.update_signal(signal.id, updates)
                if success:
                    print(f"     [OK] Updated {signal.symbol}: ₹{price}")
                else:
                    print(f"     [FAIL] Ledger update failed for {signal.id}")
            else:
                print(f"     [WARN] Could not resolve price for {signal.symbol}: {res['status']}")
        except Exception as e:
            print(f"     [ERR] {signal.symbol}: {e}")

if __name__ == "__main__":
    asyncio.run(refresh())
