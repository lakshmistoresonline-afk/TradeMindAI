import numpy as np
import pandas as pd
from typing import List

class DrawdownService:
    """
    Workstream 10: Standardized Drawdown Calculation.
    Resolves discrepancies between MD reporting and JSON forensics.
    """

    @staticmethod
    def calculate_portfolio_drawdown(equity_curve: List[float]) -> float:
        """
        Calculates maximum drawdown from a time-series equity curve.
        Metric: Portfolio Mark-to-Market Drawdown.
        """
        if not equity_curve: return 0.0

        series = pd.Series(equity_curve)
        peaks = series.expanding(min_periods=1).max()
        drawdowns = (series / peaks) - 1

        return abs(float(drawdowns.min() * 100))

    @staticmethod
    def calculate_trade_sequence_drawdown(returns_pct: List[float]) -> float:
        """
        Calculates maximum drawdown based on a sequence of trade returns.
        Metric: Trade Sequence Drawdown.
        """
        if not returns_pct: return 0.0

        # Convert to growth curve: [0.05, -0.02] -> [1.05, 1.029]
        growth = (1 + pd.Series(returns_pct) / 100).cumprod()
        peaks = growth.expanding(min_periods=1).max()
        drawdowns = (growth / peaks) - 1

        return abs(float(drawdowns.min() * 100))
