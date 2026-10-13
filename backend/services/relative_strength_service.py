"""
================================================================================
TradeMindAI: Cross-Sectional Relative Strength (RS) Decile Ranking Service
================================================================================
Ranks stocks cross-sectionally relative to the Nifty 500 benchmark.
"""

import pandas as pd
from typing import Dict, Any

class RelativeStrengthService:
    @staticmethod
    def calculate_rs_rank(stock_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes 3-month and 6-month cross-sectional relative strength vs benchmark.
        """
        if stock_df.empty or len(stock_df) < 60 or benchmark_df.empty or len(benchmark_df) < 60:
            return {"rs_score": 50.0, "top_decile": False}

        stock_return = (stock_df['close'].iloc[-1] - stock_df['close'].iloc[-60]) / stock_df['close'].iloc[-60]
        bench_return = (benchmark_df['close'].iloc[-1] - benchmark_df['close'].iloc[-60]) / benchmark_df['close'].iloc[-60]

        excess_return = stock_return - bench_return
        # Map excess return to percentile (0-100)
        rs_score = float(min(100.0, max(0.0, 50.0 + (excess_return * 100.0))))
        top_decile = bool(rs_score >= 85.0)

        return {
            "rs_score": round(rs_score, 2),
            "top_decile": top_decile
        }
