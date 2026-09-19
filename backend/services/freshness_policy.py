import datetime
from datetime import timezone
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
        now = datetime.datetime.now(timezone.utc)

        # Normalize timestamp to UTC if naive
        if timestamp.tzinfo is None:
            compare_ts = timestamp.replace(tzinfo=timezone.utc)
        else:
            compare_ts = timestamp

        # Future timestamp detection (Phase 3 Integrity)
        if compare_ts > now + datetime.timedelta(seconds=60):
            return "INVALID_FUTURE"

        age = (now - compare_ts).total_seconds()

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

        now = datetime.datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            compare_ts = timestamp.replace(tzinfo=timezone.utc)
        else:
            compare_ts = timestamp

        return {
            "status": status,
            "age_seconds": (now - compare_ts).total_seconds(),
            "timestamp": compare_ts.isoformat()
        }

