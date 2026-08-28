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
from backend.services.price_resolver import PriceResolver

async def audit():
    print("[*] STEP 1: Fetching non-resolved signals from Neon...")
    repo = container.ios_repo

    all_signals = await repo.get_all_live_signals()
    # Filter for active/waiting
    active = [s for s in all_signals if s.status in ["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"]]

    print(f"[*] Identified {len(active)} active signals for auditing.")

    updated_count = 0
    for sig in active:
        try:
            print(f"   [Auditing] {sig.symbol} ({sig.id})...")

            # 1. Resolve Current Price using Step 2C Resolver
            # This ensures derivatives use instrument_id and spot is separate
            price_res = await PriceResolver.resolve_current_price(sig)

            sig.current_price = price_res["current_price"]
            sig.underlying_price = price_res["underlying_price"]
            sig.normalized_current_price = price_res.get("normalized_current_price")
            sig.current_price_timestamp = price_res["timestamp"]
            sig.price_status = price_res["status"]
            sig.price_source = price_res["source"]
            sig.price_source = price_res["source"]

            # 2. Fetch History for Lifecycle Evaluation
            # We use the instrument_id for derivatives if available
            fetch_sym = sig.instrument_id or sig.symbol
            interval = "1d"
            if sig.timeframe == "INTRADAY": interval = "15m"

            df = await container.provider.fetch_history(fetch_sym, period="1mo", interval=interval)

            if df.empty:
                print(f"      [!] No history found for {fetch_sym}. Skipping.")
                # Still save the updated current price
                await repo.save_live_signal(sig)
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
