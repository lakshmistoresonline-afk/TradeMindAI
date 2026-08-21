import os
import sys
import asyncio
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.core.postgres import ShadowSignalDB, ShadowEventDB, ShadowScanDiagnosticDB, SessionLocal, init_db
from backend.services.outcome_engine import OutcomeEngine
from backend.services.market_calendar import IndianMarketCalendar
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

class ShadowEngineV2:
    VERSION = "v2.2-SHADOW"
    DATA_DIR = Path("data/results/step4_5")
    PORTFOLIO_FILE = DATA_DIR / "shadow_portfolio.json"

    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.portfolio = self._load_portfolio()
        init_db()

    def _load_portfolio(self) -> Dict[str, Any]:
        if self.PORTFOLIO_FILE.exists():
            with open(self.PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
        return {
            "cash": 1000000.0,
            "equity": 1000000.0,
            "realized_pnl": 0.0,
            "starting_capital": 1000000.0,
            "last_updated": datetime.utcnow().isoformat()
        }

    def _save_portfolio(self):
        self.portfolio["last_updated"] = datetime.utcnow().isoformat()
        with open(self.PORTFOLIO_FILE, 'w') as f:
            json.dump(self.portfolio, f, indent=4)

    async def run_cycle(self, mode="intraday"):
        start_time = time.time()
        scan_ts = datetime.utcnow()
        session = IndianMarketCalendar.get_current_session(scan_ts)

        print(f"[*] Starting Step 4.5.2 Shadow Engine [{scan_ts}] | Mode: {mode.upper()} | Session: {session}")

        # 1. Resolve Outcomes & Reconcile Positions (Always run)
        await self.audit_open_positions()

        cycle_metrics = {
            "scanned": 0,
            "signals": 0,
            "rejected": 0,
            "trades": 0,
            "latency_ms": 0,
            "session": session
        }

        # 2. Scan Universe for Diagnostics and Potential Trades
        diagnostics = []
        for symbol in NIFTY_200_CONSTITUENTS:
            diag_entry = {
                "symbol": symbol,
                "scan_timestamp": scan_ts,
                "threshold": 0.52,
                "model_version": "v2.2",
                "signal_decision": "REJECTED",
                "rejection_reason": "OTHER"
            }

            try:
                stock = await container.repository.get_stock_by_symbol(symbol)
                features_list = await container.data_platform_repo.get_features_by_range(
                    symbol, scan_ts - timedelta(days=7), scan_ts
                )

                if not stock or not features_list:
                    diag_entry.update({"stale_data_status": "INVALID_DATA", "rejection_reason": "INVALID_DATA"})
                else:
                    last_f = features_list[-1]
                    status, age = IndianMarketCalendar.get_data_freshness_status(last_f.date)
                    avg_vol = stock.avg_volume or 0

                    # Performance Inference for EVERY symbol (Diagnostic requirement)
                    ml_res = await container.ml_service.predict_with_champion(symbol, last_f.features)
                    prob_up = ml_res.get("metadata", {}).get("calibrated_probability_up", 0.5)
                    direction = "LONG" if prob_up >= 0.5 else "SHORT"
                    score = prob_up if direction == "LONG" else (1.0 - prob_up)

                    diag_entry.update({
                        "market_data_timestamp": last_f.date,
                        "data_age_hours": age,
                        "stale_data_status": status,
                        "liquidity_status": "PASS" if avg_vol >= 10_000_000 else "FAIL",
                        "signal_score": score,
                        "model_version": ml_res.get("model_version", "v2.2")
                    })

                    # Evaluate Rejection Reason (Prioritize Session/Freshness)
                    if session != "OPEN":
                        diag_entry["rejection_reason"] = "MARKET_CLOSED"
                    elif status == "STALE_MARKET_DATA":
                        diag_entry["rejection_reason"] = "STALE_MARKET_DATA"
                    elif avg_vol < 10_000_000:
                        diag_entry["rejection_reason"] = "INSUFFICIENT_LIQUIDITY"
                    elif score < 0.52:
                        diag_entry["rejection_reason"] = "WEAK_EDGE"
                    else:
                        # Passed filters
                        diag_entry["signal_decision"] = "SIGNAL_GENERATED"
                        cycle_metrics["signals"] += 1

                        # Only enter if in Intraday mode (Double safety)
                        if mode == "intraday" and session == "OPEN":
                            if self.can_enter_position(symbol):
                                signal = await container.signal_engine.generate_signal(symbol, "EQUITY", "SWING")
                                if signal:
                                    await self.enter_position(signal)
                                    cycle_metrics["trades"] += 1
                                else:
                                    diag_entry["rejection_reason"] = "SIGNAL_ENGINE_FILTER"
                                    diag_entry["signal_decision"] = "REJECTED"
                            else:
                                diag_entry["rejection_reason"] = "PORTFOLIO_CAPACITY"
                                diag_entry["signal_decision"] = "REJECTED"

            except Exception as e:
                diag_entry.update({"rejection_reason": "OTHER", "signal_decision": "REJECTED"})

            diagnostics.append(diag_entry)
            cycle_metrics["scanned"] += 1

        self._save_diagnostics(diagnostics)
        cycle_metrics["latency_ms"] = int((time.time() - start_time) * 1000)
        self._save_portfolio()

        self._log_event("SHADOW_CYCLE_COMPLETE", cycle_metrics)
        print(f"[SUCCESS] Cycle Complete. Mode: {mode.upper()}. Scanned: {cycle_metrics['scanned']}. Signals: {cycle_metrics['signals']}.")

    def _save_diagnostics(self, diagnostics: List[Dict[str, Any]]):
        with SessionLocal() as session:
            for d in diagnostics:
                diag = ShadowScanDiagnosticDB(
                    symbol=d["symbol"],
                    scan_timestamp=d["scan_timestamp"],
                    market_data_timestamp=d.get("market_data_timestamp"),
                    data_age_hours=d.get("data_age_hours"),
                    signal_score=d.get("signal_score"),
                    threshold=d["threshold"],
                    liquidity_status=d.get("liquidity_status"),
                    stale_data_status=d.get("stale_data_status"),
                    signal_decision=d["signal_decision"],
                    rejection_reason=d["rejection_reason"],
                    model_version=d["model_version"]
                )
                session.add(diag)
            session.commit()

    def can_enter_position(self, symbol: str) -> bool:
        with SessionLocal() as session:
            active_count = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').count()
            if active_count >= 10: return False
            existing = session.query(ShadowSignalDB).filter(ShadowSignalDB.symbol == symbol, ShadowSignalDB.status == 'ACTIVE').first()
            if existing: return False
        return True

    async def enter_position(self, signal):
        risk_per_trade = self.portfolio["equity"] * 0.01
        price_risk = abs(signal.entry_price - signal.stop_loss_price)
        if price_risk == 0: return
        qty = int(risk_per_trade / price_risk)
        if qty <= 0: return
        cost = signal.entry_price * qty
        if cost > self.portfolio["cash"]:
            qty = int(self.portfolio["cash"] / signal.entry_price)
            if qty <= 0: return

        with SessionLocal() as session:
            db_sig = ShadowSignalDB(
                id=signal.id, timestamp=signal.timestamp, symbol=signal.symbol, direction=signal.direction,
                raw_probability=signal.raw_probability, calibrated_probability=signal.calibrated_probability,
                expected_value=signal.expected_value, entry_price=signal.entry_price,
                target_price=signal.target_price, stop_price=signal.stop_loss_price,
                strategy_version=self.VERSION, model_version=signal.model_version,
                status="ACTIVE", provenance_json=json.dumps({"qty": qty, "entry_value": signal.entry_price * qty, "shadow_only": True})
            )
            session.add(db_sig)
            session.commit()

        self.portfolio["cash"] -= (signal.entry_price * qty)
        print(f"   [ENTRY] {signal.symbol} Qty: {qty} @ {signal.entry_price}")

    async def audit_open_positions(self):
        with SessionLocal() as session:
            active_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
            for sig in active_signals:
                prices = await container.repository.get_recent_prices(sig.symbol, limit=200)
                if not prices: continue

                df = pd.DataFrame([p.model_dump() for p in prices])
                df.set_index('date', inplace=True)
                df.sort_index(inplace=True)
                df.columns = [c.capitalize() for c in df.columns]

                from backend.domain.models.ios import LiveSignal
                sig_obj = LiveSignal(
                    id=sig.id, symbol=sig.symbol, timestamp=sig.timestamp,
                    entry_price=sig.entry_price, target_price=sig.target_price, stop_loss_price=sig.stop_price,
                    direction=sig.direction, status="ACTIVE", conviction=sig.calibrated_probability*100,
                    rating="BUY", timeframe="SWING"
                )

                outcome = OutcomeEngine.evaluate_outcome(sig_obj, df[df.index > sig.timestamp])

                if outcome["status"] in ["TARGET_HIT", "STOP_LOSS", "EXPIRED"]:
                    try: prov = json.loads(sig.provenance_json)
                    except:
                        import ast
                        try: prov = ast.literal_eval(sig.provenance_json)
                        except: prov = {}

                    qty = prov.get("qty", 1)
                    exit_price = outcome["outcome_price"]
                    gross_pnl = (exit_price - sig.entry_price) * qty if sig.direction == "LONG" else (sig.entry_price - exit_price) * qty
                    slippage_pct = 0.001
                    cost_pct = 0.0007
                    slip_cost = (sig.entry_price * qty * slippage_pct) + (exit_price * qty * slippage_pct)
                    trans_cost = (sig.entry_price * qty * cost_pct) + (exit_price * qty * cost_pct)
                    net_pnl = gross_pnl - slip_cost - trans_cost

                    sig.status = outcome["status"]
                    sig.outcome_timestamp = outcome["outcome_date"]
                    sig.realized_return = outcome["profit_pct"]
                    sig.slippage = slip_cost
                    sig.transaction_cost = trans_cost
                    sig.net_return = (net_pnl / (sig.entry_price * qty)) * 100 if qty > 0 else 0

                    self.portfolio["cash"] += (sig.entry_price * qty) + net_pnl
                    self.portfolio["realized_pnl"] += net_pnl
                    print(f"   [EXIT] {sig.symbol} -> {sig.status} PnL: {net_pnl:.2f}")

            # Recalculate Equity
            current_pos_val = 0
            active_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
            for s in active_signals:
                try: prov = json.loads(s.provenance_json)
                except:
                    import ast
                    try: prov = ast.literal_eval(s.provenance_json)
                    except: prov = {}
                qty = prov.get("qty", 1)
                stock = await container.repository.get_stock_by_symbol(s.symbol)
                current_pos_val += (stock.last_price or s.entry_price) * qty
            self.portfolio["equity"] = self.portfolio["cash"] + current_pos_val
            session.commit()

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        with SessionLocal() as session:
            event = ShadowEventDB(
                event_type=event_type, timestamp=datetime.utcnow(),
                strategy_version=self.VERSION, payload_json=json.dumps(data)
            )
            session.add(event)
            session.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="intraday", choices=["intraday", "eod"])
    args = parser.parse_args()

    engine = ShadowEngineV2()
    asyncio.run(engine.run_cycle(mode=args.mode))
