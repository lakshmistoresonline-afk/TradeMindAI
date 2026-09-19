import datetime
from datetime import timezone
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal
from backend.services.freshness_policy import FreshnessPolicy

class SignalValidatorService:
    """
    Institutional Signal Publication Gate (Phase 4 Final Hardening).
    Enforces strict data quality and risk criteria before a signal becomes visible to users.
    """

    @staticmethod
    def validate_publication(signal: LiveSignal) -> Dict[str, Any]:
        """
        Validates whether a signal is eligible for production release.
        """
        issues = []
        now = datetime.datetime.now(timezone.utc)

        # 1. Freshness Audit (Canonical Policy)
        freshness = FreshnessPolicy.get_status(signal.data_timestamp)
        if freshness == "STALE":
            issues.append("STALE_DATA: Market data is too old for new signal generation.")
        elif freshness == "UNAVAILABLE":
            issues.append("MISSING_DATA: Data timestamp is missing or invalid.")

        # 2. Risk Geometry Audit
        if not signal.entry_price or not signal.target_price or not signal.stop_price:
             issues.append("INCOMPLETE_PLAN: Missing entry, target, or stop loss.")
        else:
            if signal.target_price == signal.entry_price or signal.stop_price == signal.entry_price:
                issues.append("INVALID_GEOMETRY: Target or Stop cannot be identical to Entry.")

            if signal.direction == "LONG":
                if signal.target_price <= signal.entry_price: issues.append("INVALID_LEVELS: Target must be above entry for Long.")
                if signal.stop_price >= signal.entry_price: issues.append("INVALID_LEVELS: Stop must be below entry for Long.")
            else:
                if signal.target_price >= signal.entry_price: issues.append("INVALID_LEVELS: Target must be below entry for Short.")
                if signal.stop_price <= signal.entry_price: issues.append("INVALID_LEVELS: Stop must be above entry for Short.")

        # 3. Intelligence Gate
        if (signal.conviction or 0) < 52:
            issues.append(f"WEAK_EDGE: Conviction {signal.conviction}% below institutional threshold (52%).")

        if not signal.provenance_id:
            issues.append("MISSING_PROVENANCE: No trace link found.")

        # 4. Symbol Verification
        if not signal.symbol or len(signal.symbol) < 2:
            issues.append("INVALID_IDENTITY: Missing or malformed symbol.")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "status": "VALIDATED" if len(issues) == 0 else "REJECTED",
            "timestamp": now.isoformat()
        }

