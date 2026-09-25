import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional

from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.services.outcome_service import OutcomeService
from backend.services.signal_ledger_service import SignalLedgerService
from backend.core.container import container

class SignalLifecycleService:
    """
    Manages the lifecycle state machine for signals (Strategy V2.4).
    Enforces valid transitions, T1 Breakeven Trailing Stop Locks, and automated auditing.
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
    def evaluate_t1_breakeven_lock(signal: LiveSignal, current_price: float) -> Optional[float]:
        """
        T1 Breakeven Trailing Stop Lock (Strategy V2.4).
        If price touches or exceeds Target 1 (T1), automatically ratchet Stop Loss
        to Breakeven (Entry Price + 0.2% buffer), securing risk-free execution for T2/T3.
        """
        if not signal or not signal.entry_price or not signal.target_price_1 or not current_price:
            return None

        # Check if T1 has been reached
        if signal.direction == "LONG" and current_price >= signal.target_price_1:
            breakeven_stop = round(signal.entry_price * 1.002, 2) # Entry + 0.2% buffer
            if not signal.stop_price or breakeven_stop > signal.stop_price:
                return breakeven_stop
        elif signal.direction == "SHORT" and current_price <= signal.target_price_1:
            breakeven_stop = round(signal.entry_price * 0.998, 2) # Entry - 0.2% buffer
            if not signal.stop_price or breakeven_stop < signal.stop_price:
                return breakeven_stop

        return None

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
        Retrieves current market data and checks for lifecycle triggers & T1 Breakeven Locks.
        """
        signal = await SignalLedgerService.get_signal(signal_id)
        if not signal or signal.status in OutcomeService.TERMINAL_STATES:
            return False

        from backend.services.market_data_service import MarketDataService

        sym = signal.underlying_symbol or signal.symbol
        price_meta = await MarketDataService.get_current_price(sym)

        if price_meta["status"] in ["STALE", "UNAVAILABLE"]:
            print(f"[Lifecycle] Audit BLOCKED for {signal.symbol}: Market data is {price_meta['status']}.")
            return False

        current_p = price_meta.get("price", 0.0)

        # Check T1 Breakeven Stop Loss Lock
        new_breakeven_stop = SignalLifecycleService.evaluate_t1_breakeven_lock(signal, current_p)
        if new_breakeven_stop:
            print(f"[Lifecycle] T1 Reached for {signal.symbol}! Ratcheting Stop Loss to Breakeven ₹{new_breakeven_stop}")
            await SignalLedgerService.update_signal(signal_id, {
                "stop_price": new_breakeven_stop,
                "stop_loss_price": new_breakeven_stop,
                "updated_at": datetime.datetime.now(timezone.utc)
            })

        # Fetch recent price action for outcome resolution
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
