import os
import sys
import asyncio
import datetime
import pandas as pd
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import SessionLocal, ShadowSignalDB
from backend.services.outcome_engine import OutcomeEngine
from backend.services.price_resolver import PriceResolver

class SignalLifecycleWorker:
    """
    Workstream 15: TRADEMIND AI Signal Lifecycle Worker.
    Periodically updates active signals, checks outcomes, and generates new V2.2 setups.
    """

    def __init__(self):
        self.repo = container.canonical_signal_repo
        self.price_resolver = PriceResolver()

    async def run_cycle(self):
        print(f"[*] Starting Signal Lifecycle Cycle: {datetime.datetime.utcnow()}")

        # 1. Update Active Signal Outcomes
        await self._process_active_signals()

        # 2. Generate New Signals
        await self._generate_new_signals()

        # 3. Mirror to Firestore (via existing sync service)
        from backend.services.shadow_sync_service import ShadowSyncService
        await ShadowSyncService.sync_to_cloud()

        print(f"[SUCCESS] Cycle complete.")

    async def _process_active_signals(self):
        """
        Updates current prices and resolves outcomes for ACTIVE shadow signals.
        """
        active_signals = await self.repo.get_active_signals()
        print(f"   [*] Auditing {len(active_signals)} active signals...")

        for sig in active_signals:
            try:
                # A. Update Current Price via Resolver
                price_res = await self.price_resolver.resolve_current_price(sig)
                if price_res["status"] == "FRESH":
                    sig.current_price = price_res["current_price"]
                    sig.price_source = price_res["source"]
                    sig.price_timestamp = price_res["timestamp"]
                    sig.price_status = "FRESH"

                # B. Outcome Check (via OutcomeEngine)
                prices = await container.repository.get_recent_prices(sig.symbol, limit=20)
                if prices:
                    df = pd.DataFrame([p.model_dump() for p in prices])
                    df.set_index('date', inplace=True)
                    df.sort_index(inplace=True)
                    df.columns = [c.capitalize() for c in df.columns]

                    future_df = df[df.index > sig.timestamp]
                    if not future_df.empty:
                        outcome = OutcomeEngine.evaluate_outcome(sig, future_df)
                        if outcome["status"] != "ACTIVE":
                            print(f"      [TERMINAL] {sig.symbol} -> {outcome['status']}")
                            sig.status = outcome["status"]
                            sig.outcome_timestamp = outcome["outcome_date"]
                            sig.exit_price = outcome["outcome_price"]
                            sig.net_pnl = outcome.get("net_profit_pct")
                            sig.pnl_percentage = outcome.get("profit_pct")
                            sig.outcome_verified = True
                            sig.exit_reason = outcome.get("time_to_outcome_label")

                # C. Save Update to Neon
                await self.repo.save_signal(sig)

            except Exception as e:
                print(f"      [!] Error processing {sig.symbol}: {e}")

    async def _generate_new_signals(self):
        """
        Runs a scan of the NIFTY-200 universe to generate new signals.
        """
        print(f"   [*] Scanning universe for new V2.2 setups...")
        stocks = await container.repository.get_all_stocks(limit=500)
        nifty200 = [s for s in stocks if s.index_membership == 'NIFTY_200']

        for stock in nifty200:
            try:
                with SessionLocal() as session:
                    exists = session.query(ShadowSignalDB).filter(
                        ShadowSignalDB.symbol == stock.symbol,
                        ShadowSignalDB.status == 'ACTIVE'
                    ).first()
                    if exists: continue

                sig = await container.signal_engine.generate_signal(stock.symbol, "EQUITY", "SWING", stock=stock)
                if sig:
                    print(f"      [NEW_SIGNAL] {stock.symbol} ({sig.direction})")
                    await self.repo.save_signal(sig)
            except Exception: pass

if __name__ == "__main__":
    worker = SignalLifecycleWorker()
    asyncio.run(worker.run_cycle())
