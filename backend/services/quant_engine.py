import pandas as pd
import numpy as np
from typing import Dict, Any, List
from backend.domain.models.data_platform import QuantMetric
from datetime import datetime

class QuantEngine:
    @staticmethod
    def calculate_metrics(symbol: str, df: pd.DataFrame, benchmark_df: pd.DataFrame = None) -> QuantMetric:
        """
        Calculates institutional risk and performance metrics.
        """
        returns = df["Close"].pct_change().dropna()

        # 1. Volatility (Annualized)
        vol = returns.std() * np.sqrt(252)

        # 2. Sharpe Ratio (Risk-free rate assumed 7% for India)
        rf = 0.07 / 252
        excess_returns = returns - rf
        sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

        # 3. Sortino Ratio (Downside deviation only)
        downside_returns = returns[returns < 0]
        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252) if not downside_returns.empty else 0

        # 4. Max Drawdown
        cum_returns = (1 + returns).cumprod()
        peak = cum_returns.expanding(min_periods=1).max()
        drawdown = (cum_returns / peak) - 1
        max_dd = drawdown.min()

        # 5. Alpha/Beta (vs Benchmark)
        alpha, beta = 0.0, 1.0
        if benchmark_df is not None:
            bench_returns = benchmark_df["Close"].pct_change().dropna()
            # Align dates
            common_idx = returns.index.intersection(bench_returns.index)
            if len(common_idx) > 30:
                s_ret = returns.loc[common_idx]
                b_ret = bench_returns.loc[common_idx]

                covariance = np.cov(s_ret, b_ret)[0][1]
                variance = np.var(b_ret)
                beta = covariance / variance if variance != 0 else 1.0
                alpha = (s_ret.mean() - beta * b_ret.mean()) * 252

        return QuantMetric(
            symbol=symbol,
            date=datetime.utcnow(),
            sharpe_ratio=float(sharpe),
            sortino_ratio=float(sortino),
            max_drawdown=float(max_dd),
            beta=float(beta),
            alpha=float(alpha),
            volatility=float(vol)
        )
