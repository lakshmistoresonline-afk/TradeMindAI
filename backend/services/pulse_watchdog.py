import datetime
from datetime import timezone
from typing import Dict, Any, Optional

class PulseWatchdog:
    """
    P1 Production Watchdog.
    Tracks health of the background Pulse loop.
    """
    _last_started: Optional[datetime.datetime] = None
    _last_completed: Optional[datetime.datetime] = None
    _last_success: Optional[datetime.datetime] = None
    _last_failed: Optional[datetime.datetime] = None
    _last_duration_ms: int = 0
    _last_error: Optional[str] = None

    @classmethod
    def report_start(cls):
        cls._last_started = datetime.datetime.now(timezone.utc)

    @classmethod
    def report_success(cls, duration_ms: int):
        cls._last_completed = datetime.datetime.now(timezone.utc)
        cls._last_success = cls._last_completed
        cls._last_duration_ms = duration_ms

    @classmethod
    def report_failure(cls, error: str):
        cls._last_completed = datetime.datetime.now(timezone.utc)
        cls._last_failed = cls._last_completed
        cls._last_error = error

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        now = datetime.datetime.now(timezone.utc)
        status = "UNKNOWN"

        if cls._last_success:
            age = (now - cls._last_success).total_seconds()
            # If market is open, we expect pulse every 5-10m.
            # 15m threshold for LATE.
            if age < 900:
                status = "HEALTHY"
            elif age < 3600:
                status = "LATE"
            else:
                status = "STALE"

        if cls._last_failed and (not cls._last_success or cls._last_failed > cls._last_success):
            status = "FAILED"

        return {
            "status": status,
            "last_pulse_started": cls._last_started.isoformat() if cls._last_started else None,
            "last_pulse_completed": cls._last_completed.isoformat() if cls._last_completed else None,
            "last_pulse_duration_ms": cls._last_duration_ms,
            "last_error": cls._last_error,
            "server_time": now.isoformat()
        }
