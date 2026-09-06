import datetime
from typing import Dict, Any, List, Optional
from backend.domain.models.ios import LiveSignal

class LifecycleService:
    """
    Workstream 5: Canonical Signal Lifecycle.
    Implements Hard Invariants and State Transitions.
    """
    TERMINAL_STATES = ["TARGET_HIT", "STOP_LOSS", "TIMEOUT", "EXPIRED", "CANCELLED"]

    @staticmethod
    def is_terminal(status: str) -> bool:
        return status in LifecycleService.TERMINAL_STATES

    @staticmethod
    def validate_transition(from_state: str, to_state: str) -> bool:
        """
        Ensures irreversible terminal states (Workstream 5).
        """
        if LifecycleService.is_terminal(from_state):
            return False # Terminal is final

        # Valid forward flows
        allowed = {
            "CREATED": ["ACTIVE", "WAITING_FOR_ENTRY", "CANCELLED"],
            "WAITING_FOR_ENTRY": ["ACTIVE", "ENTRY_TRIGGERED", "CANCELLED", "EXPIRED"],
            "ENTRY_TRIGGERED": ["ACTIVE", "CANCELLED"],
            "ACTIVE": ["TARGET_HIT", "STOP_LOSS", "TIMEOUT", "CANCELLED"]
        }

        return to_state in allowed.get(from_state, [])

    @staticmethod
    def audit_active_breach(signal: LiveSignal, current_price: float) -> Optional[str]:
        """
        Checks if an ACTIVE signal should have already hit a terminal state.
        Workstream 5.
        """
        if not current_price or signal.status != "ACTIVE": return None

        if signal.direction == "LONG":
            if current_price >= (signal.target_price or float('inf')): return "TARGET_HIT"
            if current_price <= (signal.stop_price or float('-inf')): return "STOP_LOSS"
        else:
            if current_price <= (signal.target_price or float('-inf')): return "TARGET_HIT"
            if current_price >= (signal.stop_price or float('inf')): return "STOP_LOSS"

        return None
