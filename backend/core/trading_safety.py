"""
================================================================================
TradeMindAI: Signals-Only Execution Guard & Database Isolation Guard (SAF-01)
================================================================================
Creates an explicit application-level policy prohibiting trade execution and
enforces database write isolation during test execution.
================================================================================
"""

from dataclasses import dataclass
from enum import Enum
from typing import NoReturn


class TradingSafetyViolation(PermissionError):
    pass


class DatabaseIsolationViolation(PermissionError):
    pass


class Operation(str, Enum):
    GENERATE_SIGNAL = "generate_signal"
    VALIDATE_SIGNAL = "validate_signal"
    PUBLISH_SIGNAL = "publish_signal"
    READ_SIGNAL = "read_signal"
    EXECUTE_ORDER = "execute_order"
    MODIFY_ORDER = "modify_order"
    CANCEL_ORDER = "cancel_order"


ALLOWED_OPERATIONS = frozenset({
    Operation.GENERATE_SIGNAL,
    Operation.VALIDATE_SIGNAL,
    Operation.PUBLISH_SIGNAL,
    Operation.READ_SIGNAL,
})


@dataclass(frozen=True)
class TradingSafetyPolicy:
    real_trading_enabled: bool = False

    def __post_init__(self):
        if self.real_trading_enabled:
            raise TradingSafetyViolation(
                "Real trading is prohibited"
            )

    def authorize(self, operation: Operation) -> None:
        if operation not in ALLOWED_OPERATIONS:
            raise TradingSafetyViolation(
                f"Operation prohibited: {operation.value}"
            )

    def execute_order(self, *args, **kwargs) -> NoReturn:
        raise TradingSafetyViolation(
            "Trade execution is permanently disabled"
        )


trading_safety = TradingSafetyPolicy()

def is_signals_only_architecture() -> bool:
    """
    Evaluates effective runtime signals-only safety invariants directly across all 5 settings:
    - REAL_TRADING must be False
    - LIVE_EXECUTION_ENABLED must be False
    - BROKER_ORDER_EXECUTION_ENABLED must be False
    - QUARANTINE_ACTIVE must be True
    - SIGNALS_ONLY_ARCHITECTURE must be True directly on settings
    Fails closed (returns False) if any setting is missing (None), invalid, or unsafe.
    """
    from backend.core.config import settings

    return (
        getattr(settings, "REAL_TRADING", None) is False and
        getattr(settings, "LIVE_EXECUTION_ENABLED", None) is False and
        getattr(settings, "BROKER_ORDER_EXECUTION_ENABLED", None) is False and
        getattr(settings, "QUARANTINE_ACTIVE", None) is True and
        getattr(settings, "SIGNALS_ONLY_ARCHITECTURE", None) is True and
        getattr(trading_safety, "real_trading_enabled", True) is False
    )

def verify_test_database_isolation(db_url: str) -> bool:
    """
    Fails closed if a test attempts to connect to or perform writes against:
    - local_operational.db
    - production PostgreSQL
    - any non-isolated database
    """
    url_lower = str(db_url).lower()
    if "local_operational.db" in url_lower:
        raise DatabaseIsolationViolation("CRITICAL DATABASE ISOLATION VIOLATION: Operational database local_operational.db is prohibited in test runs!")
    if "postgresql" in url_lower and "test" not in url_lower:
        raise DatabaseIsolationViolation("CRITICAL DATABASE ISOLATION VIOLATION: Production PostgreSQL database is prohibited in test runs!")
    if ":memory:" in url_lower or "test" in url_lower or "tmp" in url_lower:
        return True
    raise DatabaseIsolationViolation(f"CRITICAL DATABASE ISOLATION VIOLATION: Non-isolated database connection ({db_url}) rejected in test runs!")
