import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional

from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.services.outcome_service import OutcomeService
from backend.services.signal_ledger_service import SignalLedgerService
from backend.core.container import container

class SignalLifecycleService:
    """
    Manages the lifecycle state machine for signals.
    Enforces valid transitions and performs automated auditing.
    """

    ALLOWED_TRANSITIONS = {
        "CREATED": ["ACTIVE", "WAITING_FOR_ENTRY", "CANCELLED"],
        "WAITING_FOR_ENTRY": ["ACTIVE", "ENTRY_TRIGGERED", "CANCELLED", "EXPIRED"],
        "ENTRY_TRIGGERED": ["ACTIVE", "CANCELLED"],
        "ACTIVE": ["TARGET_HIT", "STOP_LOSS", "TIMEOUT", "EXPIRED", "CANCELLED", "AMBIGUOUS"],
        "TARGET_HIT": [],
        "STOP_LOSS": [],
        "EXPIRED": [],
        "CANCELLED": [],
        "TIMEOUT": [],
        "AMBIGUOUS": []
    }

    @staticmethod
    async def transition_signal(signal_id: str, new_status: str, updates: Optional[Dict[str, Any]] = None) -> bool:
        signal = await SignalLedgerService.get_signal(signal_id)
        if not signal:
            return False

        current_status = signal.status
        if new_status not in SignalLifecycleService.ALLOWED_TRANSITIONS.get(current_status, []):
            print(f"[Lifecycle] Invalid transition: {current_status} -> {new_status}")
            return False

        full_updates = updates or {}
        full_updates["status"] = new_status
        full_updates["updated_at"] = datetime.datetime.now(timezone.utc)

        if new_status in OutcomeService.TERMINAL_STATES:
            full_updates["lifecycle_state"] = "TERMINAL"
            full_updates["exit_at"] = datetime.datetime.now(timezone.utc)


        return await SignalLedgerService.update_signal(signal_id, full_updates)

    @staticmethod
    async def audit_signal(signal_id: str) -> bool:
        """
        Retrieves current market data and checks for lifecycle triggers.
        Harden: Blocks mutation if data is STALE. (Phase 4).
        """
        signal = await SignalLedgerService.get_signal(signal_id)
        if not signal or signal.status in OutcomeService.TERMINAL_STATES:
            return False

        # 1. Freshness Check (Phase 4 Hardening)
        from backend.services.market_data_service import MarketDataService
        from backend.services.freshness_policy import FreshnessPolicy

        # Use underlying symbol for horizon evaluation if derivative
        sym = signal.underlying_symbol or signal.symbol
        price_meta = await MarketDataService.get_current_price(sym)

        if price_meta["status"] in ["STALE", "UNAVAILABLE"]:
            print(f"[Lifecycle] Audit BLOCKED for {signal.symbol}: Market data is {price_meta['status']}.")
            return False

        # 2. Fetch recent price action for outcome resolution
        try:
            provider = container.provider
            history = await provider.get_history(signal.symbol, start_date=signal.timestamp)

            if history.empty:
                 return False

            outcome = OutcomeService.evaluate_signal_outcome(signal, history)

            if outcome["status"] != signal.status:
                await SignalLifecycleService.transition_signal(signal_id, outcome["status"], outcome)
                return True
        except Exception as e:
            print(f"[Lifecycle] Audit failed for {signal.symbol}: {e}")

        return False
