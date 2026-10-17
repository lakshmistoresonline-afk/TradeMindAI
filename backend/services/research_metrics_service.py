import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.metrics import brier_score_loss

class ResearchMetricsService:
    """
    Phases 28-30 & Phase 9.2.7: Canonical Research Metrics, Fail-Closed Provenance Audit, and Population Separation.
    Authoritative Rules:
    - TARGET_HIT means a win.
    - STOP_LOSS means a loss.
    - EXPIRED is excluded from win/loss metrics and directional financial aggregates.
    - Explicitly separates outcome_status from financial_status, calibration_status, and provenance status.
    - Partial P&L Completeness Policy: If any eligible directional outcome has missing, NaN, or non-finite P&L,
      financial_status is INCOMPLETE_DATA, overall status is PARTIALLY_VERIFIED, and net_pnl/expectancy/profit_factor return None.
    - Zero gross loss yields profit_factor None (preventing infinite or misleading values).
    - Strict Brier score validation: accepts only finite probabilities in [0, 1] and binary outcomes {0, 1}.
    - Provenance Audit: Fail-closed verification requiring outcome_verified=True AND evaluation_mode in {"LIVE", "PAPER", "PRODUCTION"}.
      Shadow, simulation, backtest, and missing metadata default to UNVERIFIED_SHADOW_SIMULATION.
    """

    @staticmethod
    def audit_signals_provenance(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs a rigorous, deterministic fail-closed audit of all signal records for provenance,
        chronology, verification status, and financial completeness.
        """
        if not records:
            return {
                "total_audited": 0,
                "valid_count": 0,
                "verified_count": 0,
                "unverified_shadow_count": 0,
                "chronology_anomaly_count": 0,
                "duplicate_count": 0,
                "incomplete_data_count": 0,
                "excluded_count": 0,
                "status": "INSUFFICIENT_EVIDENCE"
            }

        seen_ids = set()
        duplicate_count = 0
        chronology_anomaly_count = 0
        unverified_shadow_count = 0
        incomplete_data_count = 0
        valid_count = 0
        verified_count = 0
        excluded_count = 0

        ACCEPTED_LIVE_MODES = {"LIVE", "PAPER", "PRODUCTION"}

        for r in records:
            rid = r.get('id')
            if rid in seen_ids:
                duplicate_count += 1
                excluded_count += 1
                continue
            if rid:
                seen_ids.add(rid)

            # Chronology check: signal_timestamp / created_at should be <= outcome_timestamp
            sig_ts = r.get('signal_timestamp') or r.get('created_at') or r.get('timestamp')
            out_ts = r.get('outcome_timestamp') or r.get('exit_timestamp')

            has_chrono_anomaly = False
            if sig_ts and out_ts:
                try:
                    created = r.get('created_at') or r.get('signal_timestamp')
                    if created and out_ts:
                        if pd.to_datetime(created) > pd.to_datetime(out_ts):
                            has_chrono_anomaly = True
                except Exception:
                    has_chrono_anomaly = True

            if has_chrono_anomaly:
                chronology_anomaly_count += 1
                excluded_count += 1
                continue

            # Financial completeness check
            net_pnl = r.get('net_pnl')
            if net_pnl is None or not isinstance(net_pnl, (int, float)) or not np.isfinite(net_pnl):
                incomplete_data_count += 1
                excluded_count += 1
                continue

            # Strict Fail-Closed Verification Check (No default verification)
            ov = r.get('outcome_verified')
            ev_mode = str(r.get('evaluation_mode', '')).upper()

            is_verified = (ov is True) and (ev_mode in ACCEPTED_LIVE_MODES)

            if is_verified:
                verified_count += 1
            else:
                unverified_shadow_count += 1

            valid_count += 1

        directional_records = [r for r in records if r.get('status') in ['TARGET_HIT', 'STOP_LOSS']]
        if not directional_records:
            status = "INSUFFICIENT_EVIDENCE"
        elif verified_count > 0 and unverified_shadow_count == 0:
            status = "VERIFIED"
        elif verified_count > 0 and unverified_shadow_count > 0:
            status = "PARTIALLY_VERIFIED"
        elif unverified_shadow_count > 0:
            status = "UNVERIFIED_SHADOW_SIMULATION"
        else:
            status = "INSUFFICIENT_EVIDENCE"

        return {
            "total_audited": len(records),
            "valid_count": valid_count,
            "verified_count": verified_count,
            "unverified_shadow_count": unverified_shadow_count,
            "chronology_anomaly_count": chronology_anomaly_count,
            "duplicate_count": duplicate_count,
            "incomplete_data_count": incomplete_data_count,
            "excluded_count": excluded_count,
            "status": status
        }

    @staticmethod
    def calculate_performance_metrics(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not signals:
            return {
                "sample_size": 0,
                "total_examined": 0,
                "verified_count": 0,
                "unverified_shadow_count": 0,
                "excluded_count": 0,
                "chronology_anomaly_count": 0,
                "duplicate_count": 0,
                "incomplete_data_count": 0,
                "eligible_directional_outcomes": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": None,
                "outcome_status": "INSUFFICIENT_EVIDENCE",
                "profit_factor": None,
                "expectancy": None,
                "net_pnl": None,
                "financial_status": "INSUFFICIENT_EVIDENCE",
                "brier_score": None,
                "calibration_status": "INSUFFICIENT_EVIDENCE",
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": "Empty signal ledger."
            }

        df = pd.DataFrame(signals)
        total_resolved = len(df)

        if 'net_pnl' in df.columns:
            df['net_pnl'] = pd.to_numeric(df['net_pnl'], errors='coerce')
        else:
            df['net_pnl'] = np.nan

        if 'status' in df.columns:
            directional_df = df[df['status'].isin(['TARGET_HIT', 'STOP_LOSS'])].copy()
        else:
            directional_df = pd.DataFrame()

        trade_count = len(directional_df)
        if trade_count == 0:
            provenance_audit = ResearchMetricsService.audit_signals_provenance(signals)
            return {
                "sample_size": total_resolved,
                "total_examined": provenance_audit["total_audited"],
                "verified_count": provenance_audit["verified_count"],
                "unverified_shadow_count": provenance_audit["unverified_shadow_count"],
                "excluded_count": provenance_audit["excluded_count"],
                "chronology_anomaly_count": provenance_audit["chronology_anomaly_count"],
                "duplicate_count": provenance_audit["duplicate_count"],
                "incomplete_data_count": provenance_audit["incomplete_data_count"],
                "eligible_directional_outcomes": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": None,
                "outcome_status": "INSUFFICIENT_EVIDENCE",
                "profit_factor": None,
                "expectancy": None,
                "net_pnl": None,
                "financial_status": "INSUFFICIENT_EVIDENCE",
                "brier_score": None,
                "calibration_status": "INSUFFICIENT_EVIDENCE",
                "status": provenance_audit["status"],
                "reason": "Ledger contains no directional outcomes (TARGET_HIT / STOP_LOSS)."
            }

        wins = int((directional_df['status'] == 'TARGET_HIT').sum())
        losses = int((directional_df['status'] == 'STOP_LOSS').sum())
        win_rate = round((wins / trade_count) * 100, 2)
        outcome_status = "VERIFIED"

        raw_pnls = directional_df['net_pnl']
        if raw_pnls.isna().any() or not np.isfinite(raw_pnls).all():
            net_pnl = None
            expectancy = None
            profit_factor = None
            financial_status = "INCOMPLETE_DATA"
            financial_reason = "Directional outcomes present but net_pnl data is missing or non-finite."
        else:
            financial_status = "VERIFIED"
            financial_reason = None
            gross_profit = float(raw_pnls[raw_pnls > 0].sum()) if not raw_pnls.empty else 0.0
            gross_loss = float(abs(raw_pnls[raw_pnls < 0].sum())) if not raw_pnls.empty else 0.0

            if gross_loss > 0:
                profit_factor = round(gross_profit / gross_loss, 2)
            else:
                profit_factor = None

            expectancy = round(float(raw_pnls.mean()), 4) if not raw_pnls.empty else None
            net_pnl = round(float(raw_pnls.sum()), 2) if not raw_pnls.empty else None

        brier = None
        calibration_status = "INSUFFICIENT_EVIDENCE"
        if 'calibrated_probability' in df.columns and 'outcome_binary' in df.columns:
            try:
                prob_s = pd.to_numeric(df['calibrated_probability'], errors='coerce')
                out_s = pd.to_numeric(df['outcome_binary'], errors='coerce')

                mask = (
                    prob_s.notna() & np.isfinite(prob_s) & (prob_s >= 0.0) & (prob_s <= 1.0) &
                    out_s.notna() & np.isfinite(out_s) & out_s.isin([0, 1, 0.0, 1.0])
                )

                valid_probs = prob_s[mask]
                valid_outs = out_s[mask]
                valid_pairs = len(valid_probs)

                if valid_pairs > 0:
                    brier = round(float(brier_score_loss(valid_outs, valid_probs)), 4)
                    if valid_pairs == total_resolved:
                        calibration_status = "VERIFIED"
                    else:
                        calibration_status = "INCOMPLETE_DATA"
            except (ValueError, TypeError, ZeroDivisionError):
                brier = None

        provenance_audit = ResearchMetricsService.audit_signals_provenance(signals)
        if provenance_audit["status"] == "UNVERIFIED_SHADOW_SIMULATION":
            overall_status = "UNVERIFIED_SHADOW_SIMULATION"
        elif outcome_status == "VERIFIED" and financial_status == "VERIFIED":
            overall_status = "VERIFIED"
        elif outcome_status == "VERIFIED":
            overall_status = "PARTIALLY_VERIFIED"
        else:
            overall_status = "INSUFFICIENT_EVIDENCE"

        return {
            "sample_size": total_resolved,
            "total_examined": provenance_audit["total_audited"],
            "verified_count": provenance_audit["verified_count"],
            "unverified_shadow_count": provenance_audit["unverified_shadow_count"],
            "excluded_count": provenance_audit["excluded_count"],
            "chronology_anomaly_count": provenance_audit["chronology_anomaly_count"],
            "duplicate_count": provenance_audit["duplicate_count"],
            "incomplete_data_count": provenance_audit["incomplete_data_count"],
            "eligible_directional_outcomes": trade_count,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "outcome_status": outcome_status,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "net_pnl": net_pnl,
            "financial_status": financial_status,
            "brier_score": brier,
            "calibration_status": calibration_status,
            "status": overall_status,
            "reason": financial_reason
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
