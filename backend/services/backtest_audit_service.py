import pandas as pd
from typing import Dict, Any, List
from backend.domain.models.ios import LiveSignal
from backend.services.outcome_engine import OutcomeEngine

class BacktestAuditService:
    """
    Workstream 19: Research Backtester (Rebuild).
    Audits backtest results for selection bias and look-ahead.
    """

    @staticmethod
    def run_forensic_backtest(
        symbol: str,
        signals: List[LiveSignal],
        price_history: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Runs backtest with strict high-fidelity ordering.
        Enforces same-candle STOP_LOSS precedence (Workstream 19).
        """
        results = []

        for sig in signals:
            # 1. Look-ahead Protection: Filter history to only allow future data
            future_data = price_history[price_history.index > sig.timestamp]

            if future_data.empty: continue

            # 2. Use Canonical OutcomeEngine for consistency
            outcome = OutcomeEngine.evaluate_outcome(sig, future_data)

            results.append({
                "signal_id": sig.id,
                "entry_time": sig.timestamp,
                "exit_time": outcome.get("outcome_date"),
                "outcome": outcome["status"],
                "net_pnl": outcome.get("net_profit_pct", 0.0),
                "is_verified": outcome.get("outcome_verified", False)
            })

        return results
