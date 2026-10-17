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
from backend.core.postgres import SessionLocal, LiveSignalDB
from backend.services.outcome_engine import OutcomeEngine
from backend.services.price_resolver import PriceResolver
from backend.services.signal_eligibility import is_eligible_buy
from backend.services.signal_ledger_service import SignalLedgerService

class SignalLifecycleWorker:
    """
    Workstream 15: TRADEMIND AI Signal Lifecycle Worker (Paginated NSE Master, Resilient & Auditable).
    Periodically updates active signals, checks outcomes, and generates new V2.2 setups across all horizons and validated NSE equities.
    Enforces strict status precedence: FAILED > BLOCKED > PARTIAL > COMPLETED.
    Queries LiveSignalDB with symbol and timeframe identity matching SignalLedgerService.
    """

    def __init__(self):
        self.repo = container.canonical_signal_repo
        self.price_resolver = PriceResolver()

    async def run_cycle(self) -> Dict[str, Any]:
        """
        Runs a complete lifecycle cycle, aggregating active signal processing, signal generation, and cloud sync.
        Returns a structured audit report with status (COMPLETED, PARTIAL, FAILED, BLOCKED) based on explicit precedence.
        """
        cycle_id = f"cycle_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.datetime.now(datetime.timezone.utc)
        print(f"[*] Starting Signal Lifecycle Cycle ({cycle_id}): {start_time}")

        report = {
            "cycle_id": cycle_id,
            "timestamp": start_time.isoformat(),
            "active_audited": 0,
            "active_errors": 0,
            "signals_generated": 0,
            "generation_errors": 0,
            "sync_success": False,
            "status": "COMPLETED",
            "reason": None
        }

        # 1. Update Active Signal Outcomes
        try:
            active_report = await self._process_active_signals()
            report["active_audited"] = active_report["audited"]
            report["active_errors"] = active_report["errors"]
            if active_report["errors"] > 0:
                report["status"] = "PARTIAL"
                report["reason"] = "Active signal audit encountered non-fatal errors."
        except Exception as e:
            report["status"] = "PARTIAL"
            report["reason"] = f"ACTIVE_SIGNALS_AUDIT_FAILED: {e}"
            print(f"   [!] Active signals audit failed: {e}")

        # 2. Generate New Signals
        try:
            gen_report = await self._generate_new_signals()
            report["signals_generated"] = gen_report["generated"]
            report["generation_errors"] = gen_report["errors"]

            gen_status = gen_report.get("status", "COMPLETED")
            if gen_status == "FAILED":
                report["status"] = "FAILED"
                report["reason"] = gen_report.get("reason")
            elif gen_status == "BLOCKED":
                if report["status"] != "FAILED":
                    report["status"] = "BLOCKED"
                report["reason"] = gen_report.get("reason")
            elif gen_status == "PARTIAL" or gen_report["errors"] > 0:
                if report["status"] not in ("FAILED", "BLOCKED"):
                    report["status"] = "PARTIAL"
                report["reason"] = gen_report.get("reason", "Signal generation encountered errors.")
        except Exception as e:
            report["status"] = "FAILED"
            report["reason"] = f"SIGNAL_GENERATION_FAILED: {e}"
            print(f"   [!] Signal generation stage failed: {e}")

        # 3. Mirror to Firestore (via existing sync service)
        try:
            from backend.services.shadow_sync_service import ShadowSyncService
            await ShadowSyncService.sync_to_cloud()
            report["sync_success"] = True
        except Exception as e:
            if report["status"] == "COMPLETED":
                report["status"] = "PARTIAL"
            report["sync_error"] = str(e)
            print(f"   [!] Cloud mirror sync notice: {e}")

        end_time = datetime.datetime.now(datetime.timezone.utc)
        report["duration_seconds"] = (end_time - start_time).total_seconds()

        if report["status"] == "COMPLETED":
            print(f"[SUCCESS] Cycle complete. Status: COMPLETED")
        else:
            print(f"[NOTICE] Cycle complete with status: {report['status']} (Reason: {report.get('reason')})")

        return report

    async def _process_active_signals(self) -> Dict[str, int]:
        active_signals = await self.repo.get_active_signals()
        print(f"   [*] Auditing {len(active_signals)} active signals...")
        audited = 0
        errors = 0

        for sig in active_signals:
            try:
                audited += 1
                price_res = await self.price_resolver.resolve_current_price(sig)
                if price_res["status"] == "FRESH":
                    sig.current_price = price_res["current_price"]
                    sig.price_source = price_res["source"]
                    sig.price_timestamp = price_res["timestamp"]
                    sig.price_status = "FRESH"

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

                await self.repo.save_signal(sig)
            except Exception as e:
                errors += 1
                print(f"      [!] Error processing {sig.symbol}: {e}")

        return {"audited": audited, "errors": errors}

    async def _generate_new_signals(self) -> Dict[str, Any]:
        """
        Runs a paginated scan of the full validated NSE equity master across all horizons,
        using LiveSignalDB and checking (symbol, timeframe) identity to allow distinct horizons to coexist.
        """
        print(f"   [*] Scanning validated NSE equity master (paginated) for new V2.2 setups across all horizons...")

        page_size = 200
        offset = 0
        stocks = []
        try:
            while True:
                batch = await container.repository.get_all_stocks(limit=page_size, offset=offset)
                if not batch:
                    break
                stocks.extend(batch)
                if len(batch) < page_size:
                    break
                offset += page_size
        except Exception as e:
            return {"generated": 0, "errors": 1, "status": "FAILED", "reason": f"PAGINATION_FAILED_AT_OFFSET_{offset}: {e}"}

        if not stocks:
            return {"generated": 0, "errors": 0, "status": "BLOCKED", "reason": "EMPTY_STOCK_MASTER"}

        horizons = ["SHORT", "SWING", "LONG"]
        generated = 0
        errors = 0

        for horizon in horizons:
            for stock in stocks:
                try:
                    with SessionLocal() as session:
                        exists = session.query(LiveSignalDB).filter(
                            LiveSignalDB.symbol == stock.symbol,
                            LiveSignalDB.timeframe == horizon,
                            LiveSignalDB.status == 'ACTIVE'
                        ).first()
                        if exists: continue

                    sig = await container.signal_engine.generate_signal(stock.symbol, "EQUITY", horizon, stock=stock)
                    if sig and is_eligible_buy(sig):
                        try:
                            await SignalLedgerService.create_signal(sig)
                            generated += 1
                            print(f"      [NEW_SIGNAL] {stock.symbol} ({horizon}) -> {sig.direction}")
                        except Exception:
                            errors += 1
                except Exception:
                    errors += 1

        scan_status = "COMPLETED" if errors == 0 else ("PARTIAL" if generated > 0 else "FAILED")
        return {"generated": generated, "errors": errors, "status": scan_status, "reason": None if errors == 0 else "Some signal generations or persistence attempts encountered errors."}

def main(argv=None) -> int:
    try:
        worker = SignalLifecycleWorker()
        report = asyncio.run(worker.run_cycle())
        status = report.get("status")
        if status in ("PARTIAL", "FAILED", "BLOCKED"):
            print(f"[ERROR] Worker cycle exited with status: {status} (Reason: {report.get('reason')})")
            return 1
        else:
            return 0
    except Exception as e:
        print(f"[CRITICAL] Worker execution crashed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
