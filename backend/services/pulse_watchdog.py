import datetime
from datetime import timezone
from typing import Dict, Any, Optional

class PulseWatchdog:
    """
    Hardened Durable Pulse Watchdog (Phase 4).
    Uses PulseExecutionDB to maintain state across process restarts.
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
        """
        Calculates health based on durable database history.
        """
        now = datetime.datetime.now(timezone.utc)

        # 1. Try to fetch last execution from DB (Neon Authority)
        try:
            from backend.core.postgres import SessionLocal, PulseExecutionDB
            with SessionLocal() as db:
                last_exec = db.query(PulseExecutionDB).order_by(PulseExecutionDB.started_at.desc()).first()
                if last_exec:
                    cls._last_started = last_exec.started_at
                    cls._last_completed = last_exec.finished_at
                    if last_exec.status == "COMPLETED":
                        cls._last_success = last_exec.finished_at
                        cls._last_duration_ms = last_exec.duration_ms
                    else:
                        cls._last_failed = last_exec.finished_at
                        cls._last_error = last_exec.last_error
        except Exception as e:
            print(f"[Watchdog] DB fetch failed: {e}")

        status = "UNKNOWN"

        if cls._last_success:
            # Normalize to UTC
            last_ok = cls._last_success if cls._last_success.tzinfo else cls._last_success.replace(tzinfo=timezone.utc)
            age = (now - last_ok).total_seconds()

            # Context-aware thresholds
            from backend.services.market_calendar import MarketCalendar
            is_open = MarketCalendar.is_market_open()

            threshold_late = 900 if is_open else 7200 # 15m vs 2h
            threshold_stale = 3600 if is_open else 86400 # 1h vs 24h

            if age < threshold_late: status = "HEALTHY"
            elif age < threshold_stale: status = "LATE"
            else: status = "STALE"

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
