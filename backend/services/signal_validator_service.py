import datetime
from typing import Dict, Any, Optional
from backend.domain.models.ios import LiveSignal

class SignalValidatorService:
    """
    Institutional Signal Publication Gate.
    Enforces strict data quality and risk criteria before a signal becomes visible to users.
    """

    @staticmethod
    def validate_publication(signal: LiveSignal) -> Dict[str, Any]:
        """
        Validates whether a signal is eligible for production release.
        """
        issues = []

        # 1. Freshness Audit
        now = datetime.datetime.utcnow()
        data_age_min = (now - signal.data_timestamp).total_seconds() / 60.0

        if data_age_min > 60:
            issues.append(f"STALE_DATA: Market data is {data_age_min:.1f}m old (Max 60m).")

        # 2. Risk Geometry Audit
        if signal.target_price == signal.entry_price or signal.stop_price == signal.entry_price:
            issues.append("INVALID_GEOMETRY: Target or Stop cannot be identical to Entry.")

        if signal.direction == "LONG":
            if signal.target_price <= signal.entry_price: issues.append("INVALID_LEVELS: Target must be above entry for Long.")
            if signal.stop_price >= signal.entry_price: issues.append("INVALID_LEVELS: Stop must be below entry for Long.")
        else:
            if signal.target_price >= signal.entry_price: issues.append("INVALID_LEVELS: Target must be below entry for Short.")
            if signal.stop_price <= signal.entry_price: issues.append("INVALID_LEVELS: Stop must be above entry for Short.")

        # 3. Conviction Gate
        if signal.conviction < 52:
            issues.append(f"WEAK_EDGE: Conviction {signal.conviction}% below institutional threshold (52%).")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "status": "VALIDATED" if len(issues) == 0 else "REJECTED",
            "timestamp": now.isoformat()
        }
