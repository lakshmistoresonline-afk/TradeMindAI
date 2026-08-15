import os
import sys
import asyncio
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine

async def audit():
    print("[*] STEP 1: Fetching non-resolved signals from Neon...")
    repo = container.ios_repo
    provider = container.provider

    all_signals = await repo.get_all_live_signals()
    # Filter for active/waiting
    active = [s for s in all_signals if s.status in ["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"]]

    print(f"[*] Identified {len(active)} active signals for auditing.")

    updated_count = 0
    for sig in active:
        try:
            print(f"   [Auditing] {sig.symbol} ({sig.id})...")

            # Fetch real future data (from signal timestamp to now)
            # We use 1D for positional/swing, 1H for short term, 15m for intraday if possible
            interval = "1d"
            if sig.timeframe == "INTRADAY": interval = "15m"

            df = await provider.fetch_history(sig.symbol, period="1mo", interval=interval)

            if df.empty:
                print(f"      [!] No history found for {sig.symbol}. Skipping.")
                continue

            outcome = OutcomeEngine.evaluate_outcome(sig, df)

            if outcome["status"] != sig.status:
                print(f"      [UPDATE] Status changed: {sig.status} -> {outcome['status']}")

                # Apply updates
                sig.status = outcome["status"]
                sig.outcome_date = outcome["outcome_date"]
                sig.outcome_price = outcome["outcome_price"]
                sig.profit_pct = outcome["profit_pct"]
                sig.mfe = outcome["mfe"]
                sig.mae = outcome["mae"]
                if outcome.get("trigger_price"):
                    sig.trigger_price = outcome["trigger_price"]
                    sig.triggered_at = outcome["triggered_at"]

                if outcome["events"]:
                    sig.events.extend(outcome["events"])

                await repo.save_live_signal(sig)
                updated_count += 1
            else:
                print(f"      [OK] Signal remains {sig.status}.")

        except Exception as e:
            print(f"      [ERROR] Failed to audit {sig.symbol}: {e}")

    print(f"\n[SUCCESS] Audit complete. {updated_count} signals resolved based on REAL MARKET DATA.")

if __name__ == "__main__":
    asyncio.run(audit())
