"""
================================================================================
TradeMindAI: Signals-Only Execution Guard (SAF-01)
================================================================================
Creates an explicit application-level policy prohibiting trade execution.
================================================================================
"""

from dataclasses import dataclass
from enum import Enum
from typing import NoReturn


class TradingSafetyViolation(PermissionError):
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
