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
