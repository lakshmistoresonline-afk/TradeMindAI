import datetime
from datetime import timezone
import pandas as pd
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from backend.core.container import container


class MarketDataService:
    """
    Authoritative Market Data Service.
    Handles real-time and recent price retrieval.
    """

    @staticmethod
    async def get_current_price(symbol: str) -> Dict[str, Any]:
        """
        Retrieves the most recent price and status.
        """
        try:
            # Try to get from stock service/provider
            stock = await container.repository.get_stock_by_symbol(symbol)
            if not stock or not stock.last_price:
                # Fallback to provider live call
                price_data = await container.provider.get_live_price(symbol)
                price = price_data.get("price")
                p_ts = price_data.get("timestamp")
                received_at = datetime.datetime.now(timezone.utc)

                from backend.services.freshness_policy import FreshnessPolicy
                status = FreshnessPolicy.get_status(p_ts)

                return {
                    "price": price,
                    "timestamp": p_ts or received_at,
                    "provider_timestamp": p_ts,
                    "received_at": received_at,
                    "source": "Live_Provider",
                    "status": status
                }

            # Canonical Freshness Policy (Phase 2 Hardening)
            from backend.services.freshness_policy import FreshnessPolicy
            status = FreshnessPolicy.get_status(stock.updated_at)

            return {
                "price": stock.last_price,
                "timestamp": stock.updated_at,
                "provider_timestamp": stock.updated_at,
                "received_at": stock.updated_at,
                "source": "SQL_Cache",
                "status": status
            }

        except Exception as e:
            print(f"[MarketData] Error fetching price for {symbol}: {e}")
            return {
                "price": None,
                "timestamp": None,
                "provider_timestamp": None,
                "received_at": datetime.datetime.now(timezone.utc),
                "source": None,
                "status": "UNAVAILABLE"
            }


    @staticmethod
    async def get_ohlc_history(symbol: str, days: int = 30) -> pd.DataFrame:
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        return await container.provider.get_history(symbol, start_date=start_date)

    @staticmethod
    async def get_market_state() -> Dict[str, Any]:
        """
        Hardened Market State Truth Model (V2.3 Production).
        Distinguishes observation, reception, and processing time.
        """
        received_at = datetime.datetime.now(timezone.utc)
        try:
            # 1. Fetch Index & VIX in parallel using YahooQuery (Resilient Bulk)
            from yahooquery import Ticker as YQTicker
            yq = YQTicker("^NSEI ^INDIAVIX")
            hist = yq.history(period="3mo")

            if hist.empty:
                return {
                    "regime": "UNKNOWN", "risk_mode": "UNKNOWN", "vix": None,
                    "status": "UNAVAILABLE", "source": "YAHOO_QUERY",
                    "observation_timestamp": None, "received_at": received_at.isoformat()
                }

            # 2. Extract Data & Timestamps
            nifty_df = pd.DataFrame()
            vix_val = None
            observation_ts = None

            if "^NSEI" in hist.index.get_level_values('symbol'):
                nifty_df = hist.xs("^NSEI", level='symbol').rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
                # Capture actual provider timestamp from index
                obs_raw = hist.index.get_level_values('date')[-1]

                # Normalize to datetime (V2.3 Robustness)
                if isinstance(obs_raw, datetime.date) and not isinstance(obs_raw, datetime.datetime):
                    observation_ts = datetime.datetime.combine(obs_raw, datetime.time.min)
                elif hasattr(obs_raw, 'to_pydatetime'):
                    observation_ts = obs_raw.to_pydatetime()
                else:
                    observation_ts = obs_raw

                if observation_ts and observation_ts.tzinfo is None:
                    observation_ts = observation_ts.replace(tzinfo=timezone.utc)

            if "^INDIAVIX" in hist.index.get_level_values('symbol'):
                vix_df = hist.xs("^INDIAVIX", level='symbol')
                # Bulk normalization (V2.3)
                vix_df = vix_df.rename(columns={c: c.capitalize() for c in vix_df.columns})
                if 'Close' in vix_df.columns and not vix_df['Close'].dropna().empty:
                    vix_val = float(vix_df['Close'].dropna().iloc[-1])

            # 3. Detect Regime
            from backend.services.ios.regime_engine import MarketRegimeEngine
            from backend.services.freshness_policy import FreshnessPolicy

            if vix_val is None or vix_val <= 0 or nifty_df.empty:
                 return {
                    "regime": "UNKNOWN", "risk_mode": "UNKNOWN", "vix": vix_val,
                    "status": "UNAVAILABLE", "source": "YAHOO_QUERY",
                    "observation_timestamp": observation_ts.isoformat() if observation_ts else None,
                    "received_at": received_at.isoformat()
                }

            regime_obj = MarketRegimeEngine.detect_regime(nifty_df, float(vix_val))
            freshness = FreshnessPolicy.get_status(observation_ts)

            return {
                "regime": regime_obj.regime,
                "risk_mode": regime_obj.risk_mode,
                "vix": float(vix_val),
                "nifty_price": float(nifty_df['Close'].iloc[-1]) if not nifty_df.empty else None,
                "sentiment_score": regime_obj.sentiment_score,
                "description": regime_obj.description,
                "observation_timestamp": observation_ts.isoformat(),
                "received_at": received_at.isoformat(),
                "calculated_at": datetime.datetime.now(timezone.utc).isoformat(),
                "source": "YAHOO_QUERY",
                "freshness": freshness,
                "status": "HEALTHY" if freshness in ["FRESH", "AGING"] else "DEGRADED"
            }

        except Exception as e:
            print(f"[MarketData] Regime detection failed: {e}")
            return {
                "regime": "ERROR", "risk_mode": "ERROR", "vix": None,
                "status": "ERROR", "error": str(e),
                "observation_timestamp": None, "received_at": received_at.isoformat()
            }




    @staticmethod
    async def sync_active_signal_prices(execution_id: Optional[str] = None):
        """
        Throttled Pulse Sync: Syncs current prices for all non-terminal signals.
        Logs forensic metrics for institutional release.
        P1: Durable Pulse Execution Ledger (Phase 3 Hardening)
        """
        from backend.core.version import GIT_SHA
        from backend.core.postgres import PulseExecutionDB, SessionLocal
        from backend.services.market_calendar import MarketCalendar

        pulse_id = execution_id or str(uuid.uuid4())
        started_at = datetime.datetime.now(timezone.utc)

        print(f"[*] MarketDataService: Throttled Pulse Sync Started (ID: {pulse_id[:8]})...")
        from backend.services.price_resolver import PriceResolver
        from backend.services.signal_ledger_service import SignalLedgerService
        from backend.services.pulse_watchdog import PulseWatchdog
        import time

        PulseWatchdog.report_start()
        stats = {

            "success": 0, "failed": 0, "total": 0,
            "start_time": time.time(), "skipped": 0, "transitions": 0,
            "fresh": 0, "aging": 0, "stale": 0, "unavailable": 0
        }

        last_error = None
        error_count = 0

        try:
            # 1. Fetch non-terminal signals
            all_signals = await container.ios_repo.get_all_live_signals()
            non_terminal = [s for s in all_signals if s.status in ["WAITING_FOR_ENTRY", "ENTRY_TRIGGERED", "ACTIVE"]]
            stats["total"] = len(non_terminal)

            if not non_terminal:
                print("   [DEBUG] No active signals to sync.")
            else:
                # P1 Bounded Concurrency (Phase 2 Hardening)
                semaphore = asyncio.Semaphore(10)

                async def process_signal(sig):
                    nonlocal last_error, error_count
                    async with semaphore:
                        try:
                            start_fetch = time.time()
                            res = await PriceResolver.resolve_current_price(sig)
                            fetch_duration = (time.time() - start_fetch) * 1000

                            p_status = res.get("status")
                            if p_status == "FRESH": stats["fresh"] += 1
                            elif p_status == "AGING": stats["aging"] += 1
                            elif p_status == "STALE": stats["stale"] += 1
                            else: stats["unavailable"] += 1

                            if p_status == "FRESH":
                                updates = {
                                    "current_price": res["current_price"],
                                    "current_price_timestamp": res["timestamp"],
                                    "current_price_source": res["source"],
                                    "current_price_status": "FRESH",
                                    "last_reconciled_at": datetime.datetime.now(timezone.utc),
                                    "pulse_execution_id": pulse_id
                                }

                                await SignalLedgerService.update_signal(sig.id, updates)
                                stats["success"] += 1

                                from backend.services.signal_lifecycle_service import SignalLifecycleService
                                changed = await SignalLifecycleService.audit_signal(sig.id)
                                if changed: stats["transitions"] += 1

                                print(f"   [SYNC_OK] {sig.symbol} | Price: {res['current_price']} | Provider: {res['source']} | Latency: {fetch_duration:.1f}ms")
                            else:
                                print(f"   [SYNC_WARN] {sig.symbol} failed resolution: {res['status']}")
                                stats["failed"] += 1
                        except Exception as sig_err:
                            print(f"   [!] Signal refresh failed for {sig.symbol}: {sig_err}")
                            stats["failed"] += 1
                            last_error = str(sig_err)
                            error_count += 1

                # Run in parallel with bounding
                await asyncio.gather(*[process_signal(s) for s in non_terminal])

            duration_ms = int((time.time() - stats["start_time"]) * 1000)
            PulseWatchdog.report_success(duration_ms)
            print(f"[+] Pulse Sync Complete: {stats['success']} OK, {stats['failed']} FAIL. Duration: {duration_ms/1000:.1f}s")


            # Durable Ledger (SQL)
            try:
                with SessionLocal() as db:
                    pulse_rec = PulseExecutionDB(
                        execution_id=pulse_id, started_at=started_at, finished_at=datetime.datetime.now(timezone.utc),
                        duration_ms=duration_ms, market_status="OPEN" if MarketCalendar.is_market_open() else "CLOSED",
                        lock_acquired=True, deployment_sha=GIT_SHA, signals_seen=stats["total"],
                        signals_processed=stats["success"] + stats["failed"], signals_updated=stats["success"],
                        signals_skipped=stats["skipped"], signals_failed=stats["failed"],
                        fresh_count=stats["fresh"], aging_count=stats["aging"], stale_count=stats["stale"],
                        unavailable_count=stats["unavailable"], lifecycle_transitions=stats["transitions"],
                        error_count=error_count, last_error=last_error, status="COMPLETED"
                    )
                    db.add(pulse_rec)
                    db.commit()
            except Exception as db_err:
                print(f"[!] Failed to record Pulse execution in SQL: {db_err}")

            # Store sync metadata in Firebase for Admin visibility (P1 Observability)
            from backend.core.database import db_client
            if db_client:
                try:
                    db_client.collection("system_metrics").document("last_price_sync").set({
                        "pulse_execution_id": pulse_id,
                        "started_at": started_at,
                        "finished_at": datetime.datetime.now(timezone.utc),
                        "duration_ms": duration_ms,
                        "signals_total": stats["total"],
                        "signals_success": stats["success"],
                        "signals_failed": stats["failed"],
                        "signals_skipped": stats["skipped"],
                        "lifecycle_transitions": stats["transitions"],
                        "status": "COMPLETED"
                    })
                except: pass

        except Exception as e:
            print(f"[!] MarketDataService: Pulse sync failed: {e}")
            from backend.services.pulse_watchdog import PulseWatchdog
            PulseWatchdog.report_failure(str(e))
            try:
                with SessionLocal() as db:

                     db.add(PulseExecutionDB(
                         execution_id=pulse_id, started_at=started_at, finished_at=datetime.datetime.now(timezone.utc),
                         status="FAILED", last_error=str(e), error_count=1
                     ))
                     db.commit()
            except: pass


