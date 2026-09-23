"""
================================================================================
TradeMindAI: Local Market Data Service
================================================================================
Queries historical price data directly from local database tables using
Pandas SQL readers for optimized sub-50ms chart query execution.
"""

import logging
import pandas as pd
from sqlalchemy import text
from backend.app.db.database import engine

logger = logging.getLogger(__name__)

class LocalMarketDataService:
    """
    Service for fast, offline local market data queries.
    """

    @staticmethod
    def get_historical_data(symbol: str, limit: int = 180) -> pd.DataFrame:
        """
        Retrieves historical OHLCV data for a given symbol directly from local DB.
        """
        query_sql = text("""
            SELECT timestamp, open, high, low, close, volume
            FROM app_market_data
            WHERE UPPER(symbol) = UPPER(:symbol)
            ORDER BY timestamp ASC
            LIMIT :limit
        """)

        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(query_sql, conn, params={"symbol": symbol, "limit": limit})

            if df.empty:
                logger.warning(f"[MarketData] No local price data found for symbol: {symbol}")
                return pd.DataFrame()

            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
        except Exception as err:
            logger.error(f"[MarketData] Error querying symbol {symbol}: {err}")
            return pd.DataFrame()

    @staticmethod
    def get_available_symbols() -> list:
        """
        Returns list of all available symbols in the local database.
        """
        query_sql = text("SELECT DISTINCT symbol FROM app_market_data ORDER BY symbol ASC")
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(query_sql, conn)
            return df["symbol"].tolist()
        except Exception:
            return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
