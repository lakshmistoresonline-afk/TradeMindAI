
import os
import sys
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import ShadowSignalDB, engine, SessionLocal
from backend.services.outcome_engine import OutcomeEngine
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

class ShadowService:
    STRATEGY_VERSION = "v2.2"
    DRAWDOWN_LIMIT = 15.0
    OBSERVATION_LOG = "validation/shadow/shadow_observations.csv"

    @staticmethod
    async def run_shadow_cycle():
        """
        Executes a full shadow trading cycle:
        1. Check current drawdown.
        2. Scan universe for signals.
        3. Persist and Log results.
        4. Audit existing signals for outcomes.
        """
        run_ts = datetime.utcnow()
        print(f"[*] Starting Shadow Cycle [{run_ts}]")

        # 1. Check Drawdown
        current_dd = ShadowService.calculate_current_drawdown()
        if current_dd > ShadowService.DRAWDOWN_LIMIT:
            print(f"[!] CRITICAL: Drawdown limit exceeded ({current_dd:.2f}%). Shadow trading halted.")
            return

        # 2. Scan Universe & Log Evaluations
        evaluations = []
        for symbol in NIFTY_200_CONSTITUENTS:
            eval_data = ShadowService._init_eval_data(symbol, run_ts)
            try:
                # Get eligibility data
                stock = await container.repository.get_stock_by_symbol(symbol)
                champion = await container.data_platform_repo.get_champion_model(symbol)

                if not champion:
                    eval_data.update({"decision": "NO_TRADE_MODEL_ERROR", "rejection_reason": "NO_MODEL_FOUND"})
                else:
                    eval_data["model_version"] = champion.version
                    features_list = await container.data_platform_repo.get_features_by_range(symbol, run_ts - timedelta(days=7), run_ts)

                    if not features_list:
                        eval_data.update({"decision": "DATA_UNAVAILABLE", "rejection_reason": "NO_FEATURES_FOUND"})
                    else:
                        last_f = features_list[-1]
                        eval_data.update({
                            "price": stock.last_price if stock else None,
                            "EMA_200": last_f.features.get("ema_200"),
                            "ATR": last_f.features.get("ATR"),
                            "liquidity": stock.avg_volume if stock else 0.0
                        })

                        # Execute Strategy
                        signal = await container.signal_engine.generate_signal(symbol, "EQUITY", "SWING")

                        if signal:
                            eval_data.update({
                                "decision": "TRADE_SIGNAL",
                                "calibrated_probability": signal.calibrated_probability,
                                "EV": signal.expected_value,
                                "direction": signal.direction,
                                "target": signal.target_price,
                                "stop": signal.stop_loss_price,
                                "data_quality_score": signal.data_quality_score
                            })
                            ShadowService.persist_shadow_signal(signal)
                        else:
                            # Rejection reason tracking
                            reason = await ShadowService._audit_rejection(symbol, stock, last_f.features)
                            eval_data.update({"decision": "NO_TRADE", "rejection_reason": reason})

            except Exception as e:
                eval_data.update({"decision": "NO_TRADE_DATA_ERROR", "rejection_reason": f"EXCEPTION: {str(e)}"})

            evaluations.append(eval_data)

        # Log Evaluations
        ShadowService._log_to_csv(evaluations)
        ShadowService._log_to_db(evaluations)

        # 3. Resolve Outcomes
        await ShadowService.audit_open_signals()

    @staticmethod
    def _log_to_db(evaluations):
        from backend.core.postgres import ShadowEventDB
        with SessionLocal() as session:
            for eval_data in evaluations:
                # Basic payload extraction
                payload = {
                    "price": eval_data.get("price"),
                    "prob": eval_data.get("calibrated_probability"),
                    "ev": eval_data.get("EV"),
                    "ema200": eval_data.get("EMA_200"),
                    "atr": eval_data.get("ATR"),
                    "liq": eval_data.get("liquidity")
                }
                event = ShadowEventDB(
                    event_type="EVALUATION",
                    symbol=eval_data["symbol"],
                    timestamp=datetime.fromisoformat(eval_data["timestamp"]),
                    strategy_version=eval_data["strategy_version"],
                    model_version=eval_data["model_version"],
                    decision=eval_data["decision"],
                    rejection_reason=eval_data["rejection_reason"],
                    payload_json=json.dumps(payload)
                )
                session.add(event)
            session.commit()
            print(f"   [DB] {len(evaluations)} events recorded to ShadowEventDB")

    @staticmethod
    def _init_eval_data(symbol, ts):
        return {
            "date": ts.date().isoformat(),
            "timestamp": ts.isoformat(),
            "symbol": symbol,
            "strategy_version": ShadowService.STRATEGY_VERSION,
            "model_version": None, "price": None, "probability": None,
            "calibrated_probability": None, "EV": None, "data_quality_score": 0.0,
            "liquidity": 0.0, "ATR": None, "EMA_200": None, "direction": None,
            "target": None, "stop": None, "decision": "UNKNOWN", "rejection_reason": None
        }

    @staticmethod
    async def _audit_rejection(symbol, stock, features) -> str:
        # Check specific gates
        if not stock: return "DATA_UNAVAILABLE"

        avg_vol = stock.avg_volume if stock.avg_volume is not None else 0.0
        if avg_vol < 10_000_000: return "INSUFFICIENT_LIQUIDITY"

        ml_res = await container.ml_service.predict_with_champion(symbol, features)
        if ml_res.get("prediction") == "NEUTRAL": return "NEUTRAL_PREDICTION"

        prob = ml_res.get("metadata", {}).get("calibrated_probability_up")
        if prob is None or prob < 0.52: return "WEAK_EDGE"

        price = stock.last_price
        if price is None: return "DATA_ERROR"

        ema200 = features.get("ema_200")
        if ema200 is None: return "DATA_ERROR"

        direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
        if (direction == "LONG" and price < ema200) or (direction == "SHORT" and price > ema200):
            return "TREND_CONFLICT"

        return "OTHER_FILTER"

    @staticmethod
    def _log_to_csv(evaluations):
        df = pd.DataFrame(evaluations)
        header = not os.path.exists(ShadowService.OBSERVATION_LOG)
        df.to_csv(ShadowService.OBSERVATION_LOG, mode='a', index=False, header=header)
        print(f"   [LOG] Evaluations recorded to {ShadowService.OBSERVATION_LOG}")

    @staticmethod
    def calculate_current_drawdown() -> float:
        with SessionLocal() as session:
            query = text("SELECT net_return FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED')")
            res = session.execute(query).fetchall()
            if not res: return 0.0
            returns = [r[0] for r in res if r[0] is not None]
            if not returns: return 0.0
            cum_returns = (1 + pd.Series(returns)/100).cumprod()
            peak = cum_returns.expanding().max()
            dd = (cum_returns / peak - 1) * 100
            return abs(float(dd.min()))

    @staticmethod
    def persist_shadow_signal(signal):
        with SessionLocal() as session:
            existing = session.query(ShadowSignalDB).filter(ShadowSignalDB.symbol == signal.symbol, ShadowSignalDB.status == 'ACTIVE').first()
            if existing: return
            db_sig = ShadowSignalDB(
                id=signal.id, timestamp=signal.timestamp, symbol=signal.symbol, direction=signal.direction,
                raw_probability=signal.raw_probability, calibrated_probability=signal.calibrated_probability,
                expected_value=signal.expected_value, data_quality_score=signal.data_quality_score,
                entry_price=signal.entry_price, target_price=signal.target_price, stop_price=signal.stop_loss_price,
                strategy_version=ShadowService.STRATEGY_VERSION, model_version=signal.model_version,
                feature_version=signal.provenance.get("feature_version", "v1.0.0"),
                regime=signal.regime, status="ACTIVE", provenance_json=str(signal.provenance)
            )
            session.add(db_sig)
            session.commit()
            print(f"   [SHADOW] Signal Persisted: {signal.symbol} {signal.direction} @ {signal.entry_price}")

    @staticmethod
    async def audit_open_signals():
        from production.reports.shadow_reporter import ShadowReporter
        from backend.core.postgres import ShadowEventDB

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
                    sig.status = outcome["status"]
                    sig.outcome_timestamp = outcome["outcome_date"]
                    sig.realized_return = outcome["profit_pct"]
                    sig.realized_mfe = outcome["mfe"]
                    sig.realized_mae = outcome["mae"]

                    friction = 0.20
                    sig.transaction_cost = 0.10
                    sig.slippage = 0.10
                    sig.net_return = outcome["profit_pct"] - friction

                    print(f"   [SHADOW] Signal Resolved: {sig.symbol} -> {sig.status} ({sig.net_return:.2f}%)")

                    # Log Event
                    event = ShadowEventDB(
                        event_type="OUTCOME_RESOLUTION",
                        signal_id=sig.id,
                        symbol=sig.symbol,
                        timestamp=datetime.utcnow(),
                        decision=sig.status,
                        payload_json=json.dumps(outcome, default=str)
                    )
                    session.add(event)
                    session.commit() # Commit before report generation

                    # Trigger Automated Reporting
                    ShadowReporter.generate_outcome_reports(sig.id)

                elif outcome["status"] == "DATA_UNAVAILABLE":
                    # If we have no data to confirm the outcome yet, keep it ACTIVE but note pending status
                    # However, if it's been active for too long with no data, we might flag as pending error
                    pass
                elif outcome["status"] == "AMBIGUOUS":
                    sig.status = "OUTCOME_PENDING"
                    sig.rejection_reason = "AMBIGUOUS_PRICE_ACTION"
                    print(f"   [SHADOW] Signal Ambiguous: {sig.symbol} -> OUTCOME_PENDING")

            session.commit()

if __name__ == "__main__":
    asyncio.run(ShadowService.run_shadow_cycle())
