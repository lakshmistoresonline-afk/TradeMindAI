
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
        1. Check production safety (SQLite forbidden).
        2. Acquire Distributed Lock (Redis).
        3. Check current drawdown.
        4. Scan universe for signals.
        5. Persist and Log results.
        6. Audit existing signals for outcomes.
        """
        # 1. Production Safety Check
        from backend.core.config import settings
        from backend.core.postgres import DATABASE_URL
        if settings.ENVIRONMENT == "production" and "sqlite" in DATABASE_URL.lower():
            print("[!] CRITICAL: PRODUCTION_SHADOW_SQLITE_FORBIDDEN. Halted.")
            return

        # 2. Acquire Distributed Lock (Redis)
        from redis import asyncio as aioredis
        is_locked = False
        redis = None
        try:
            redis = aioredis.from_url(settings.REDIS_URL)
            lock_key = "lock:shadow_engine_cycle"
            # Try to acquire lock for 45 minutes
            is_locked = await redis.set(lock_key, "LOCKED", ex=2700, nx=True)
            if not is_locked:
                print("[INFO] Shadow cycle already in progress (Locked). Skipping.")
                return
        except Exception as e:
            print(f"[WARN] Redis connection failed: {e}. Proceeding without lock (Local Mode).")
            is_locked = True # Allow execution locally if redis fails

        try:
            run_ts = datetime.utcnow()
            print(f"[*] Starting Shadow Cycle [{run_ts}]")

            # 0. Market Session Check (Phase 7.9)
            from backend.services.market_calendar import IndianMarketCalendar
            session_type = IndianMarketCalendar.get_current_session(run_ts)
            print(f"[*] Current Market Session: {session_type}")

            if session_type in ["WEEKEND", "HOLIDAY"]:
                print(f"[INFO] Market is {session_type}. Skipping cycle.")
                # We still sync to ensure dashboard freshness
                from backend.services.shadow_sync_service import ShadowSyncService
                await ShadowSyncService.sync_to_cloud()
                return

            # Record Heartbeat
            from production.shadow.shadow_heartbeat import ShadowHeartbeat
            ShadowHeartbeat.record_heartbeat("ENGINE_RUNNING")

            # 3. Check Drawdown
            current_dd = ShadowService.calculate_current_drawdown()
            if current_dd > ShadowService.DRAWDOWN_LIMIT:
                print(f"[!] CRITICAL: Drawdown limit exceeded ({current_dd:.2f}%). Shadow trading halted.")
                return

            # 4. Fetch Operational Data & Update Live Prices
            print("[*] Syncing authoritative prices (Bulk)...")
            stocks_list = await container.repository.get_all_stocks(limit=500)
            stock_map = {s.symbol: s for s in stocks_list}

            try:
                from yahooquery import Ticker
                mapped_symbols = [container.provider._map_symbol(s) for s in NIFTY_200_CONSTITUENTS]
                symbol_map = {container.provider._map_symbol(s): s for s in NIFTY_200_CONSTITUENTS}
                t = Ticker(mapped_symbols)
                live_prices = t.price

                with SessionLocal() as session:
                    from backend.core.postgres import StockDB
                    for mapped_sym, p_info in live_prices.items():
                        symbol = symbol_map.get(mapped_sym)
                        if not symbol or not isinstance(p_info, dict): continue
                        curr = p_info.get('regularMarketPrice')
                        if curr:
                            session.query(StockDB).filter(StockDB.symbol == symbol).update({
                                "last_price": curr,
                                "updated_at": datetime.utcnow()
                            })
                            if symbol in stock_map:
                                stock_map[symbol].last_price = curr
                                stock_map[symbol].updated_at = datetime.utcnow()
                    session.commit()
                print("[+] Operational store updated with live prices.")
            except Exception as e:
                print(f"[WARN] Live price update failed: {e}")

            # 5. Scan Universe (Only if market is OPEN)
            evaluations = []
            provider_name = container.provider.__class__.__name__
            if session_type == "OPEN":
                champions_list = await container.data_platform_repo.get_all_champion_models()
                champion_map = {c.symbol: c for c in champions_list}

                print(f"[*] Scanning {len(NIFTY_200_CONSTITUENTS)} symbols...")

                for symbol in NIFTY_200_CONSTITUENTS:
                    eval_data = ShadowService._init_eval_data(symbol, run_ts)
                    try:
                        # Use pre-fetched data
                        stock = stock_map.get(symbol)
                        champion = champion_map.get(symbol)

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
                                signal = await container.signal_engine.generate_signal(
                                    symbol, "EQUITY", "SWING",
                                    stock=stock,
                                    features_list=features_list,
                                    current_dd=current_dd,
                                    champion=champion,
                                    save_prediction=False
                                )

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
                                    reason = await ShadowService._audit_rejection(symbol, stock, last_f.features, champion)
                                    eval_data.update({"decision": "NO_TRADE", "rejection_reason": reason})

                    except Exception as e:
                        eval_data.update({"decision": "NO_TRADE_DATA_ERROR", "rejection_reason": f"EXCEPTION: {str(e)}"})

                    evaluations.append(eval_data)

                # 6. Log Evaluations (Bulk)
                ShadowService._log_to_csv(evaluations)
                ShadowService._log_to_db(evaluations)
                ShadowService._log_diagnostics(evaluations, provider_name)
            else:
                print(f"[INFO] Market is {session_type}. Skipping signal generation.")

            # 6. Resolve Outcomes (Always run unless weekend/holiday)
            await ShadowService.audit_open_signals()

            # 7. Async Firestore Sync (Best-effort, non-blocking)
            try:
                from backend.services.shadow_sync_service import ShadowSyncService
                # Use a timeout to ensure sync doesn't hang the process
                await asyncio.wait_for(ShadowSyncService.sync_to_cloud(), timeout=30)
            except asyncio.TimeoutError:
                print("[WARN] Firestore Sync timed out. Continuing...")
            except Exception as e:
                print(f"[WARN] Firestore Sync failed: {e}")

            print(f"[*] Shadow Cycle Complete [{datetime.utcnow()}]")
            ShadowHeartbeat.record_heartbeat("ENGINE_IDLE")

        finally:
            # Release Lock
            try:
                if redis:
                    if is_locked: await redis.delete(lock_key)
                    await redis.close()
            except: pass

    @staticmethod
    def _log_diagnostics(evaluations, provider_name):
        from backend.core.postgres import ShadowScanDiagnosticDB
        with SessionLocal() as session:
            for ev in evaluations:
                diag = ShadowScanDiagnosticDB(
                    symbol=ev["symbol"],
                    scan_timestamp=datetime.fromisoformat(ev["timestamp"]),
                    signal_score=ev.get("calibrated_probability"),
                    signal_decision=ev["decision"],
                    rejection_reason=ev["rejection_reason"],
                    model_version=ev.get("model_version"),
                    provider_name=provider_name,
                    provider_latency_ms=0 # Mock
                )
                session.add(diag)
            session.commit()

    @staticmethod
    def _log_to_db(evaluations):
        from backend.core.postgres import ShadowEventDB
        from backend.core.config import settings
        eval_mode = "LIVE_SHADOW" if settings.ENVIRONMENT in ["production", "shadow"] else "TEST"

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
                    payload_json=json.dumps(payload),
                    evaluation_mode=eval_mode
                )
                session.add(event)
            session.commit()
            print(f"   [DB] {len(evaluations)} events recorded to ShadowEventDB [Mode: {eval_mode}]")

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
    async def _audit_rejection(symbol, stock, features, champion) -> str:
        # Check specific gates
        if not stock: return "DATA_UNAVAILABLE"

        avg_vol = stock.avg_volume if stock.avg_volume is not None else 0.0
        if avg_vol < 10_000_000: return "INSUFFICIENT_LIQUIDITY"

        # Optimized: Pass pre-loaded champion and disable persistence
        ml_res = await container.ml_service.predict_with_champion(symbol, features, champion=champion, save=False)
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
        # Workstream 20: Use Canonical Repository
        repo = container.canonical_signal_repo

        async def _run_persist():
            # 1. Save Provenance (if available in signal object)
            if signal.provenance and isinstance(signal.provenance, dict) and 'provenance_id' in signal.provenance:
                await repo.save_provenance(signal.provenance)

            # 2. Save Signal
            await repo.save_signal(signal)

            # 3. Mirror to Firestore (Downstream)
            try:
                from backend.core.database import get_db
                db_client = get_db()
                if db_client:
                    # Minimal mirror for UI reactivity
                    db_client.collection("shadow_signals").document(signal.id).set(signal.model_dump(exclude={'provenance'}))
            except Exception as e:
                print(f"   [SYNC] Firestore mirror failed for {signal.symbol}: {e}")

            # 4. Phase 7A: Audit Trail (Workstream 12)
            from backend.core.postgres import SessionLocal, ShadowEventDB
            with SessionLocal() as session:
                event = ShadowEventDB(
                    event_type="SIGNAL_GENERATED",
                    signal_id=signal.id,
                    symbol=signal.symbol,
                    timestamp=datetime.utcnow(),
                    strategy_version=ShadowService.STRATEGY_VERSION,
                    decision="TRADE_SIGNAL",
                    evaluation_mode=signal.evaluation_mode
                )
                session.add(event)
                session.commit()

            print(f"   [SHADOW] Signal Persisted: {signal.symbol} {signal.direction} @ {signal.entry_price} [Mode: {signal.evaluation_mode}]")

        asyncio.create_task(_run_persist())

    @staticmethod
    async def audit_open_signals():
        from production.reports.shadow_reporter import ShadowReporter
        from backend.core.postgres import ShadowEventDB
        from yahooquery import Ticker
        import pytz

        print("[*] Auditing Lifecycle for Open Signals (Forensic)...")
        repo = container.canonical_signal_repo

        active_signals = await repo.get_active_signals()
        if not active_signals:
            print("   [INFO] No active signals to audit.")
            return

        # 1. Bulk Fetch Intraday Data (1m for high precision)
        symbols = [s.symbol for s in active_signals]
        provider = container.provider
        mapped_symbols = [provider._map_symbol(s) for s in symbols]

        try:
            t = Ticker(mapped_symbols)
            # Fetch 5-day 1m history to ensure coverage of signal lifetimes (usually 1-2 days)
            hist_df = t.history(period="5d", interval="1m")
        except Exception as e:
            print(f"   [!] Failed to fetch intraday data for audit: {e}")
            return

        if hist_df.empty:
            print("   [!] No intraday data returned for audit.")
            return

        # 2. Process each signal
        for sig in active_signals:
            mapped_sym = provider._map_symbol(sig.symbol)

            try:
                # Extract data for this symbol
                if mapped_sym not in hist_df.index.get_level_values(0):
                    continue

                df_sym = hist_df.xs(mapped_sym, level=0).copy()
                df_sym.index = pd.to_datetime(df_sym.index)
                col_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
                df_sym = df_sym.rename(columns=col_map)

                outcome = OutcomeEngine.evaluate_outcome(sig, df_sym)

                if outcome["status"] in ["TARGET_HIT", "STOP_LOSS", "EXPIRED"]:
                    # Record Terminal State
                    sig.status = outcome["status"]
                    sig.outcome_timestamp = outcome["outcome_date"]
                    sig.exit_price = outcome["outcome_price"]
                    sig.exit_timestamp = outcome["outcome_date"] # Ledger 2.0 alignment

                    # Reconciliation & Performance
                    sig.net_pnl = outcome.get("net_profit_pct", outcome["profit_pct"] - 0.20)
                    sig.outcome_verified = outcome.get("outcome_verified", False)
                    sig.pnl_percentage = outcome["profit_pct"]
                    sig.mae = outcome.get("mae", 0.0)
                    sig.mfe = outcome.get("mfe", 0.0)
                    sig.verification_level = 4 # LIVE_SHADOW_VERIFIED
                    sig.lifecycle_state = "TERMINAL"

                    print(f"   [TERMINAL] {sig.symbol} -> {sig.status} @ {sig.outcome_timestamp} (Net: {sig.net_pnl:.2f}%) [Verified: {sig.outcome_verified}]")

                    # Persist Update
                    await repo.save_signal(sig)

                    # Log Persistence Event
                    with SessionLocal() as session:
                        event = ShadowEventDB(
                            event_type="OUTCOME_RESOLUTION",
                            signal_id=sig.id,
                            symbol=sig.symbol,
                            timestamp=datetime.utcnow(),
                            decision=sig.status,
                            payload_json=json.dumps(outcome, default=str)
                        )
                        session.add(event)
                        session.commit()

                    # Trigger Reporting
                    try: ShadowReporter.generate_outcome_reports(sig.id)
                    except: pass

            except Exception as e:
                print(f"   [!] Error auditing {sig.symbol}: {e}")

        print("[SUCCESS] Lifecycle Audit Complete.")

if __name__ == "__main__":
    asyncio.run(ShadowService.run_shadow_cycle())
