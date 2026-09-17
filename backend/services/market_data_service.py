import datetime
import pandas as pd
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

            # Check staleness
            age = (datetime.datetime.utcnow() - stock.updated_at).total_seconds() if stock.updated_at else 999999
            status = "FRESH" if age < 300 else ("AGING" if age < 3600 else "STALE")

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
        """
        try:
            # 1. Fetch VIX
            vix = await container.provider.get_ltp("INDIAVIX")

            # 2. Fetch Index for Regime
            index_df = await container.provider.fetch_history("NIFTY", period="1y")

            # 3. Detect Regime
            from backend.services.ios.regime_engine import MarketRegimeEngine
            # Create a mock VIX df for engine
            vix_df = pd.DataFrame([{"Close": vix}]) if vix else pd.DataFrame()
            regime_obj = MarketRegimeEngine.detect_regime(index_df, vix_df)

            return {
                "regime": regime_obj.regime,
                "risk_mode": regime_obj.risk_mode,
                "vix": vix or 14.5,
                "sentiment_score": regime_obj.sentiment_score,
                "description": regime_obj.description,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "status": "HEALTHY" if vix else "DEGRADED"
            }
        except Exception as e:
            print(f"[MarketData] Regime detection failed: {e}")
            return {
                "regime": "SIDEWAYS",
                "risk_mode": "NEUTRAL",
                "vix": 14.5,
                "status": "ERROR",
                "error": str(e)
            }

    @staticmethod
    async def sync_active_signal_prices():
        """
        Background Worker: Syncs current prices for all non-terminal signals.
        Institutional 4.0 Hardening.
        """
        print("[*] MarketDataService: Syncing Active Signal Prices...")
        from backend.services.price_resolver import PriceResolver
        from backend.services.signal_ledger_service import SignalLedgerService

        try:
            # 1. Fetch all signals that need a price update
            all_signals = await container.ios_repo.get_all_live_signals()
            non_terminal = [s for s in all_signals if s.status in ["WAITING_FOR_ENTRY", "ENTRY_TRIGGERED", "ACTIVE"]]

            if not non_terminal:
                print("   [DEBUG] No active signals to sync.")
                return

            for signal in non_terminal:
                res = await PriceResolver.resolve_current_price(signal)
                if res["status"] == "FRESH":
                    updates = {
                        "current_price": res["current_price"],
                        "current_price_timestamp": res["timestamp"],
                        "current_price_source": res["source"],
                        "current_price_status": "FRESH"
                    }
                    await SignalLedgerService.update_signal(signal.id, updates)

            print(f"[+] MarketDataService: Successfully synced {len(non_terminal)} prices.")
        except Exception as e:
            print(f"[!] MarketDataService: Price sync failed: {e}")
