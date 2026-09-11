import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.core.container import container
from backend.domain.models.stock import StockPrice

class HistoricalDataService:
    """
    Authoritative Historical Data Pipeline.
    Handles source -> raw -> validation -> canonical.
    """

    @staticmethod
    async def get_validated_history(
        symbol: str,
        start_date: datetime.datetime,
        end_date: Optional[datetime.datetime] = None
    ) -> pd.DataFrame:
        """
        Fetches history from the provider and validates it against canonical rules.
        """
        provider = container.provider
        df = await provider.get_history(symbol, start_date=start_date, end_date=end_date)

        if df.empty:
            return pd.DataFrame()

        # Validation logic (Phase 4)
        # 1. Reject price <= 0
        df = df[(df['Open'] > 0) & (df['High'] > 0) & (df['Low'] > 0) & (df['Close'] > 0)]

        # 2. Reject invalid OHLC (High < Low)
        df = df[df['High'] >= df['Low']]

        # 3. Close outside valid OHLC
        df = df[(df['Close'] >= df['Low']) & (df['Close'] <= df['High'])]

        # 4. Remove future timestamps
        now = datetime.datetime.now(df.index.tz) if df.index.tz else datetime.datetime.now()
        df = df[df.index <= now]

        # 5. Remove duplicates
        df = df[~df.index.duplicated(keep='first')]

        return df

    @staticmethod
    async def calculate_coverage(symbol: str, expected_years: int = 5) -> Dict[str, Any]:
        """
        Calculates actual trading days vs expected (Phase 5).
        """
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=expected_years * 365)

        df = await HistoricalDataService.get_validated_history(symbol, start_date, end_date)

        if df.empty:
            return {
                "coverage_percentage": 0.0,
                "actual_trading_days": 0,
                "expected_trading_days": expected_years * 252, # Approx
                "missing_days": expected_years * 252
            }

        actual_days = len(df)
        # Expected trading days in India is approx 250 per year
        expected_days = expected_years * 250
        coverage = (actual_days / expected_days) * 100

        return {
            "coverage_percentage": round(min(100.0, coverage), 2),
            "actual_trading_days": actual_days,
            "expected_trading_days": expected_days,
            "historical_start": df.index.min().isoformat(),
            "historical_end": df.index.max().isoformat(),
            "missing_days": max(0, expected_days - actual_days)
        }
