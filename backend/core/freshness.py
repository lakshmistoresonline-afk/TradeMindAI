from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class FreshnessPolicy:
    """
    Authoritative Institutional Freshness Policy (Institutional 1.5).
    """

    FRESH_MINUTES = 15
    AGING_MINUTES = 120
    STALE_MINUTES = 120

    @classmethod
    def get_status(cls, updated_at: Optional[datetime]) -> str:
        if not updated_at:
            return "UNAVAILABLE"

        now = datetime.utcnow()
        # Handle timezone-aware datetimes by converting to UTC
        if updated_at.tzinfo:
            updated_at = updated_at.astimezone(None).replace(tzinfo=None)

        age_seconds = (now - updated_at).total_seconds()

        if age_seconds < (cls.FRESH_MINUTES * 60):
            return "FRESH"
        elif age_seconds < (cls.AGING_MINUTES * 60):
            return "AGING"
        else:
            return "STALE"

    @classmethod
    def get_metadata(cls, updated_at: Optional[datetime]) -> Dict[str, Any]:
        status = cls.get_status(updated_at)
        age_seconds = 0
        if updated_at:
            if updated_at.tzinfo:
                updated_at = updated_at.astimezone(None).replace(tzinfo=None)
            age_seconds = (datetime.utcnow() - updated_at).total_seconds()

        return {
            "status": status,
            "age_seconds": round(age_seconds, 1),
            "updated_at": updated_at.isoformat() if updated_at else None,
            "policy": "INSTITUTIONAL_1.5"
        }
