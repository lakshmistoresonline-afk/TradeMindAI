import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.metrics import brier_score_loss, roc_auc_score, log_loss

class ResearchMetricsService:
    """
    Phases 28-30: Canonical Research Metrics and Segmentation.
    """

    @staticmethod
    def calculate_performance_metrics(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not signals:
            return {"trade_count": 0, "win_rate": 0.0, "net_pnl": 0.0}

        df = pd.DataFrame(signals)

        # 1. Trade Outcomes
        trade_count = len(df)
        wins = len(df[df['net_pnl'] > 0])
        losses = len(df[df['net_pnl'] <= 0])
        win_rate = (wins / trade_count) * 100 if trade_count > 0 else 0.0

        gross_profit = df[df['net_pnl'] > 0]['net_pnl'].sum()
        gross_loss = abs(df[df['net_pnl'] <= 0]['net_pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        expectancy = (df['net_pnl'].mean()) if not df.empty else 0.0
        net_pnl = df['net_pnl'].sum()

        # 2. Probability Calibration (Phase 27)
        brier = 0.0
        if 'calibrated_probability' in df.columns and 'outcome_binary' in df.columns:
            try:
                brier = brier_score_loss(df['outcome_binary'], df['calibrated_probability'])
            except: pass

        return {
            "sample_size": trade_count,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy": round(expectancy, 4),
            "net_pnl": round(net_pnl, 2),
            "brier_score": round(brier, 4)
        }

    @staticmethod
    def segment_performance(df: pd.DataFrame, segment_col: str) -> Dict[str, Any]:
        """
        Segment by Sector, Regime, Direction, etc. (Phase 29)
        """
        if segment_col not in df.columns: return {}

        segments = {}
        for name, group in df.groupby(segment_col):
            segments[str(name)] = ResearchMetricsService.calculate_performance_metrics(group.to_dict('records'))

        return segments
