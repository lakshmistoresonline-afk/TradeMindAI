"""
================================================================================
TradeMindAI: Institutional Signal Publication Gate & Risk Validator (v3.0)
================================================================================
Enforces strict data quality, direction integrity, price finiteness, and risk
geometry criteria before a signal becomes eligible for publication.
Rejects non-directional predictions (NEUTRAL/UNAVAILABLE) and geometry violations.
================================================================================
"""

import datetime
from datetime import timezone
from typing import Dict, Any, Optional
import numpy as np

from backend.domain.models.ios import LiveSignal
from backend.services.freshness_policy import FreshnessPolicy

class SignalValidatorService:
    """
    Institutional Signal Publication Gate & Risk Geometry Validator.
    Enforces strict data quality, directional validity, price finiteness, and risk criteria.
    """

    ALLOWED_DIRECTIONS = {"LONG", "BUY", "SHORT", "SELL"}

    @staticmethod
    def validate_publication(signal: LiveSignal) -> Dict[str, Any]:
        """
        Validates whether a signal is eligible for production release.
        """
        issues = []
        now = datetime.datetime.now(timezone.utc)

        # 1. Direction Integrity Audit
        raw_dir = getattr(signal, "direction", None)
        if not raw_dir or str(raw_dir).strip().upper() not in SignalValidatorService.ALLOWED_DIRECTIONS:
            issues.append(f"NON_DIRECTIONAL_PREDICTION: Direction '{raw_dir}' is invalid or non-directional (NEUTRAL/UNAVAILABLE).")

        # 2. Freshness Audit (Canonical Policy)
        freshness = FreshnessPolicy.get_status(getattr(signal, "data_timestamp", None))
        if freshness == "STALE":
            issues.append("STALE_DATA: Market data is too old for new signal generation.")
        elif freshness == "UNAVAILABLE":
            issues.append("MISSING_DATA: Data timestamp is missing or invalid.")

        # 3. Price Finiteness & Positive Value Audit
        ep = getattr(signal, "entry_price", None)
        tp = getattr(signal, "target_price", None)
        sp = getattr(signal, "stop_price", None)

        if ep is None or tp is None or sp is None:
            issues.append("INCOMPLETE_PLAN: Missing entry, target, or stop loss price.")
        else:
            try:
                ep_f, tp_f, sp_f = float(ep), float(tp), float(sp)
                if not (np.isfinite(ep_f) and np.isfinite(tp_f) and np.isfinite(sp_f)):
                    issues.append("NON_FINITE_PRICES: Entry, target, or stop price contains NaN or Infinity.")
                elif ep_f <= 0 or tp_f <= 0 or sp_f <= 0:
                    issues.append("NON_POSITIVE_PRICES: Entry, target, or stop price must be positive.")
                else:
                    # Risk Geometry Audit
                    risk_dist = abs(ep_f - sp_f)
                    reward_dist = abs(tp_f - ep_f)

                    if risk_dist <= 1e-4:
                        issues.append("ZERO_RISK_DISTANCE: Stop price cannot be identical to entry price.")
                    else:
                        rr_ratio = reward_dist / risk_dist
                        if not np.isfinite(rr_ratio) or rr_ratio < 1.0:
                            issues.append(f"SUBOPTIMAL_RISK_REWARD: Risk/Reward ratio {rr_ratio:.2f} is below minimum 1.0 threshold.")

                    dir_upper = str(raw_dir).strip().upper() if raw_dir else ""
                    if dir_upper in ("LONG", "BUY"):
                        if tp_f <= ep_f:
                            issues.append("INVALID_LEVELS: Target must be above entry for Long.")
                        if sp_f >= ep_f:
                            issues.append("INVALID_LEVELS: Stop must be below entry for Long.")
                    elif dir_upper in ("SHORT", "SELL"):
                        if tp_f >= ep_f:
                            issues.append("INVALID_LEVELS: Target must be below entry for Short.")
                        if sp_f <= ep_f:
                            issues.append("INVALID_LEVELS: Stop must be above entry for Short.")
            except (ValueError, TypeError):
                issues.append("INVALID_PRICE_TYPE: Non-numeric price value provided.")

        # 4. Conviction & Intelligence Gate
        conviction = getattr(signal, "conviction", 0) or 0
        if conviction < 52:
            issues.append(f"WEAK_EDGE: Conviction {conviction}% below institutional threshold (52%).")

        if not getattr(signal, "provenance_id", None):
            issues.append("MISSING_PROVENANCE: No trace link found.")

        # 5. Symbol Verification
        sym = getattr(signal, "symbol", "")
        if not sym or len(str(sym).strip()) < 2:
            issues.append("INVALID_IDENTITY: Missing or malformed symbol.")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "status": "VALIDATED" if len(issues) == 0 else "REJECTED",
            "timestamp": now.isoformat()
        }
