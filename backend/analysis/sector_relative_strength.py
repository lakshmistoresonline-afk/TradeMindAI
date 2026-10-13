"""
Sector & Intermarket Relative Strength Matrix
Computes cross-sectional momentum and relative strength against sector ETFs.
"""

import pandas as pd
from typing import Dict, Any

class SectorRelativeStrength:
    @staticmethod
    def calculate_relative_strength(stock_prices: pd.Series, sector_prices: pd.Series, benchmark_prices: pd.Series, period: int = 65) -> Dict[str, Any]:
        """
        Calculates Stock vs Sector and Sector vs Benchmark Relative Strength.
        """
        if len(stock_prices) < period or len(sector_prices) < period or len(benchmark_prices) < period:
            return {"stock_rs": 1.0, "sector_rs": 1.0, "outperforming": True}

        stock_return = float(stock_prices.iloc[-1] / stock_prices.iloc[-period] - 1)
        sector_return = float(sector_prices.iloc[-1] / sector_prices.iloc[-period] - 1)
        benchmark_return = float(benchmark_prices.iloc[-1] / benchmark_prices.iloc[-period] - 1)

        stock_rs = (1.0 + stock_return) / (1.0 + sector_return)
        sector_rs = (1.0 + sector_return) / (1.0 + benchmark_return)

        outperforming = bool(stock_rs >= 1.02 and sector_rs >= 1.0)

        return {
            "stock_rs": stock_rs,
            "sector_rs": sector_rs,
            "stock_return": stock_return,
            "sector_return": sector_return,
            "outperforming": outperforming
        }
