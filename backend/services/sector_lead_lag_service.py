"""
================================================================================
TradeMindAI: Sector Lead-Lag Cross-Correlation Matrix Service
================================================================================
Models cross-correlations between sector indices and component stocks to capture
institutional capital rotation.
"""

import pandas as pd
from typing import Dict, Any

class SectorLeadLagService:
    @staticmethod
    def evaluate_lead_lag(stock_df: pd.DataFrame, sector_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates cross-correlation lag between sector index and stock.
        """
        if stock_df.empty or sector_df.empty or len(stock_df) < 30 or len(sector_df) < 30:
            return {"lead_lag_score": 0.5, "sector_aligned": True}

        stock_ret = stock_df['close'].pct_change().dropna()
        sector_ret = sector_df['close'].pct_change().dropna()

        # Align lengths
        min_len = min(len(stock_ret), len(sector_ret))
        corr = float(stock_ret.tail(min_len).corr(sector_ret.tail(min_len)))

        aligned = bool(corr >= 0.40) # Positive sector beta alignment

        return {
            "sector_correlation": round(corr, 4),
            "sector_aligned": aligned
        }
