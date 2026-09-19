import datetime
import pandas as pd
import asyncio
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
                return {
                    "price": price_data.get("price"),
                    "timestamp": datetime.datetime.utcnow(),
                    "source": "Live_Provider",
                    "status": "FRESH" if price_data.get("price") else "UNAVAILABLE"
                }

            # Canonical Freshness Policy (Phase 2 Hardening)
            from backend.services.freshness_policy import FreshnessPolicy
            status = FreshnessPolicy.get_status(stock.updated_at)

            return {
                "price": stock.last_price,
                "timestamp": stock.updated_at,
                "source": "SQL_Cache",
                "status": status
            }

        except Exception as e:
            print(f"[MarketData] Error fetching price for {symbol}: {e}")
            return {"price": None, "timestamp": None, "source": None, "status": "UNAVAILABLE"}

    @staticmethod
    async def get_ohlc_history(symbol: str, days: int = 30) -> pd.DataFrame:
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        return await container.provider.get_history(symbol, start_date=start_date)

    @staticmethod
    async def get_market_state() -> Dict[str, Any]:
        """
        Final Hardening: Single source of truth for Market Regime and VIX.
        No fabricated data fallback (Phase 2 Hardening).
        """
        try:
            # 1. Fetch VIX (Hardened for ^INDIAVIX)
            vix = await container.provider.get_ltp("INDIAVIX")
            if not vix:
                # Fallback check for ticker with hat
                vix = await container.provider.get_ltp("^INDIAVIX")

            # 2. Fetch Index for Regime
            index_df = await container.provider.fetch_history("NIFTY", period="1y")

            # 3. Detect Regime
            from backend.services.ios.regime_engine import MarketRegimeEngine

            if vix is None or vix <= 0:
                 return {
                    "regime": "UNKNOWN",
                    "risk_mode": "UNKNOWN",
                    "vix": None,
                    "status": "UNAVAILABLE",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }

            regime_obj = MarketRegimeEngine.detect_regime(index_df, float(vix))

            return {
                "regime": regime_obj.regime,
                "risk_mode": regime_obj.risk_mode,
                "vix": float(vix),
                "sentiment_score": regime_obj.sentiment_score,
                "description": regime_obj.description,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "status": "HEALTHY"
            }
        except Exception as e:
            print(f"[MarketData] Regime detection failed: {e}")
            return {
                "regime": "ERROR",
                "risk_mode": "ERROR",
                "vix": None,
                "status": "ERROR",
                "error": "Market source connectivity failure.",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }


    @staticmethod
    async def sync_active_signal_prices(execution_id: Optional[str] = None):
        """
        Throttled Pulse Sync: Syncs current prices for all non-terminal signals.
        Logs forensic metrics for institutional release.
        """
        pulse_id = execution_id or str(uuid.uuid4())
        print(f"[*] MarketDataService: Throttled Pulse Sync Started (ID: {pulse_id[:8]})...")
        from backend.services.price_resolver import PriceResolver
        from backend.services.signal_ledger_service import SignalLedgerService
        import time

        try:
            # 1. Fetch non-terminal signals
            all_signals = await container.ios_repo.get_all_live_signals()
            non_terminal = [s for s in all_signals if s.status in ["WAITING_FOR_ENTRY", "ENTRY_TRIGGERED", "ACTIVE"]]

            if not non_terminal:
                print("   [DEBUG] No active signals to sync.")
                return

            stats = {
                "success": 0, "failed": 0, "total": len(non_terminal),
                "start_time": time.time(), "skipped": 0, "transitions": 0
            }

            # P1 Bounded Concurrency (Phase 2 Hardening)
            semaphore = asyncio.Semaphore(10)

            async def process_signal(sig):
                async with semaphore:
                    try:
                        start_fetch = time.time()
                        res = await PriceResolver.resolve_current_price(sig)
                        fetch_duration = (time.time() - start_fetch) * 1000

                        if res["status"] == "FRESH":
                            updates = {
                                "current_price": res["current_price"],
                                "current_price_timestamp": res["timestamp"],
                                "current_price_source": res["source"],
                                "current_price_status": "FRESH",
                                "last_reconciled_at": datetime.datetime.utcnow(),
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

            # Run in parallel with bounding
            await asyncio.gather(*[process_signal(s) for s in non_terminal])


            duration = time.time() - stats["start_time"]
            print(f"[+] Pulse Sync Complete: {stats['success']} OK, {stats['failed']} FAIL. Duration: {duration:.1f}s")

            # Store sync metadata in Firebase for Admin visibility (P1 Observability)
            from backend.core.database import db_client
            if db_client:
                try:
                    db_client.collection("system_metrics").document("last_price_sync").set({
                        "pulse_execution_id": pulse_id,
                        "started_at": datetime.datetime.fromtimestamp(stats["start_time"]),
                        "finished_at": datetime.datetime.utcnow(),
                        "duration_ms": int(duration * 1000),
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

