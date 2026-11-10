"""
================================================================================
TradeMindAI: Canonical Freshness Policy Service (v3.0)
================================================================================
One source of truth for market data age classification and staleness audit.
Handles both datetime objects and ISO-formatted timestamp strings safely.
================================================================================
"""

import datetime
from datetime import timezone
from typing import Dict, Any, Optional, Union

class FreshnessPolicy:
    """
    Canonical Freshness Policy.
    One source of truth for data age classification.
    """
    FRESH_THRESHOLD = 900   # 15 minutes
    AGING_THRESHOLD = 7200  # 120 minutes

    @classmethod
    def _parse_timestamp(cls, timestamp: Optional[Union[datetime.datetime, str]]) -> Optional[datetime.datetime]:
        if not timestamp:
            return None
        if isinstance(timestamp, str):
            try:
                # Handle ISO format strings
                cleaned_str = timestamp.replace("Z", "+00:00")
                return datetime.datetime.fromisoformat(cleaned_str)
            except Exception:
                return None
        if isinstance(timestamp, datetime.datetime):
            return timestamp
        return None

    @classmethod
    def get_status(cls, timestamp: Optional[Union[datetime.datetime, str]]) -> str:
        parsed_ts = cls._parse_timestamp(timestamp)
        if not parsed_ts:
            return "UNAVAILABLE"

        # Ensure UTC comparison
        now = datetime.datetime.now(timezone.utc)

        # Normalize timestamp to UTC if naive
        if parsed_ts.tzinfo is None:
            compare_ts = parsed_ts.replace(tzinfo=timezone.utc)
        else:
            compare_ts = parsed_ts.astimezone(timezone.utc)

        # Future timestamp detection
        if compare_ts > now + datetime.timedelta(seconds=60):
            return "INVALID_FUTURE"

        age = (now - compare_ts).total_seconds()

        if age < cls.FRESH_THRESHOLD:
            return "FRESH"
        if age < cls.AGING_THRESHOLD:
            return "AGING"
        return "STALE"

    @classmethod
    def get_metadata(cls, timestamp: Optional[Union[datetime.datetime, str]]) -> Dict[str, Any]:
        parsed_ts = cls._parse_timestamp(timestamp)
        status = cls.get_status(parsed_ts)
        if not parsed_ts:
            return {"status": status, "age_seconds": None}

        now = datetime.datetime.now(timezone.utc)
        if parsed_ts.tzinfo is None:
            compare_ts = parsed_ts.replace(tzinfo=timezone.utc)
        else:
            compare_ts = parsed_ts.astimezone(timezone.utc)

        age = (now - compare_ts).total_seconds()
        return {
            "status": status,
            "age_seconds": round(age, 2),
            "timestamp_utc": compare_ts.isoformat()
        }
