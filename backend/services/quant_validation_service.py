import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from scipy import stats

class QuantitativeValidationService:
    """
    Phase 7E: Research-grade Quantitative Validation System.
    Implements Workstreams 1, 2, 3, 4, 7, 11.
    """

    @staticmethod
    def calculate_probability_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
        """
        Calculates calibration and accuracy metrics (Brier, LogLoss, ROC-AUC).
        """
        if len(y_true) == 0:
            return {"status": "INSUFFICIENT_DATA"}

        brier = brier_score_loss(y_true, y_prob)
        ll = log_loss(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.5

        return {
            "brier_score": round(float(brier), 4),
            "log_loss": round(float(ll), 4),
            "roc_auc": round(float(auc), 4),
            "sample_size": len(y_true)
        }

    @staticmethod
    def generate_reliability_curve(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 5) -> List[Dict[str, Any]]:
        """
        Generates reliability curve data (Predicted vs Actual probability buckets).
        Workstream 3.
        """
        from sklearn.calibration import calibration_curve
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)

        # Calculate counts per bin for Workstream 3 "Mark insufficient sample size"
        bins = np.linspace(0., 1. + 1e-8, n_bins + 1)
        binids = np.digitize(y_prob, bins) - 1
        bin_counts = np.bincount(binids, minlength=len(bins))

        results = []
        for i in range(len(prob_true)):
            results.append({
                "predicted_prob": round(float(prob_pred[i]), 3),
                "actual_win_rate": round(float(prob_true[i]), 3),
                "sample_size": int(bin_counts[i]),
                "status": "VALID" if bin_counts[i] >= 5 else "INSUFFICIENT_SAMPLE"
            })
        return results

    @staticmethod
    def validate_ev_correlation(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates correlation between Predicted EV and Realized Net P&L.
        Workstream 4.
        """
        if df.empty or 'predicted_ev' not in df.columns or 'net_pnl' not in df.columns:
            return {"status": "INSUFFICIENT_DATA"}

        # Pearson Correlation
        corr, p_val = stats.pearsonr(df['predicted_ev'], df['net_pnl'])
        # Spearman Rank Correlation (Workstream 4)
        rank_corr, rank_p = stats.spearmanr(df['predicted_ev'], df['net_pnl'])

        return {
            "pearson_correlation": round(float(corr), 4),
            "spearman_rank_correlation": round(float(rank_corr), 4),
            "p_value": round(float(p_val), 4),
            "is_significant": p_val < 0.05
        }

    @staticmethod
    def outlier_sensitivity_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates performance variants excluding top/bottom outliers.
        Workstream 14.
        """
        if len(df) < 5: return {"status": "INSUFFICIENT_DATA"}

        sorted_pnl = df['net_pnl'].sort_values()

        results = {
            "full_sample_net": round(df['net_pnl'].sum(), 2),
            "without_best_1": round(df['net_pnl'].sum() - sorted_pnl.iloc[-1], 2),
            "without_best_3": round(df['net_pnl'].sum() - sorted_pnl.iloc[-3:].sum(), 2),
            "without_worst_1": round(df['net_pnl'].sum() - sorted_pnl.iloc[0], 2),
            "without_worst_3": round(df['net_pnl'].sum() - sorted_pnl.iloc[:3].sum(), 2)
        }
        return results

    @staticmethod
    def detect_model_drift(ref_dist: np.ndarray, current_dist: np.ndarray) -> Dict[str, Any]:
        """
        Detects distribution shift using Kolmogorov-Smirnov test.
        Workstream 8.
        """
        if len(ref_dist) == 0 or len(current_dist) == 0:
            return {"status": "INSUFFICIENT_DATA"}

        ks_stat, p_val = stats.ks_2samp(ref_dist, current_dist)

        return {
            "ks_statistic": round(float(ks_stat), 4),
            "p_value": round(float(p_val), 4),
            "drift_detected": p_val < 0.05,
            "status": "DRIFTED" if p_val < 0.05 else "HEALTHY"
        }
