import datetime
from typing import Dict, Any, Optional

class FreshnessPolicy:
    """
    P0 Canonical Freshness Policy.
    One source of truth for data age classification.
    """
    FRESH_THRESHOLD = 900 # 15 minutes
    AGING_THRESHOLD = 7200 # 120 minutes

    @classmethod
    def get_status(cls, timestamp: Optional[datetime.datetime]) -> str:
        if not timestamp:
            return "UNAVAILABLE"

        # Ensure UTC comparison
        if timestamp.tzinfo:
            now = datetime.datetime.now(datetime.timezone.utc)
        else:
            now = datetime.datetime.utcnow()

        age = (now - timestamp).total_seconds()

        if age < cls.FRESH_THRESHOLD:
            return "FRESH"
        if age < cls.AGING_THRESHOLD:
            return "AGING"
        return "STALE"

    @classmethod
    def get_metadata(cls, timestamp: Optional[datetime.datetime]) -> Dict[str, Any]:
        status = cls.get_status(timestamp)
        if not timestamp:
            return {"status": status, "age_seconds": None}

        if timestamp.tzinfo:
            now = datetime.datetime.now(datetime.timezone.utc)
        else:
            now = datetime.datetime.utcnow()

        return {
            "status": status,
            "age_seconds": (now - timestamp).total_seconds(),
            "timestamp": timestamp.isoformat()
        }
