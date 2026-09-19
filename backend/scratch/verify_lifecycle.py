import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_lifecycle_service import SignalLifecycleService

async def test_lifecycle():
    print("CLAIM: Deterministic lifecycle state machine")
    print("-" * 60)

    cases = [
        ("CREATED", "WAITING_FOR_ENTRY", True),
        ("CREATED", "ACTIVE", True),
        ("CREATED", "CANCELLED", True),
        ("WAITING_FOR_ENTRY", "ACTIVE", True),
        ("WAITING_FOR_ENTRY", "EXPIRED", True),
        ("ACTIVE", "TARGET_HIT", True),
        ("ACTIVE", "STOP_LOSS", True),
        ("ACTIVE", "AMBIGUOUS", True),
        # Forbidden
        ("TARGET_HIT", "ACTIVE", False),
        ("STOP_LOSS", "ACTIVE", False),
        ("AMBIGUOUS", "ACTIVE", False),
        ("EXPIRED", "ACTIVE", False),
        ("CREATED", "TARGET_HIT", False),
    ]

    from backend.services.signal_ledger_service import SignalLedgerService
    original_get_signal = SignalLedgerService.get_signal
    original_update_signal = SignalLedgerService.update_signal

    for start, target, allowed in cases:
        mock_signal = MagicMock()
        mock_signal.status = start

        SignalLedgerService.get_signal = MagicMock(return_value=asyncio.Future())
        SignalLedgerService.get_signal.return_value.set_result(mock_signal)

        SignalLedgerService.update_signal = MagicMock(return_value=asyncio.Future())
        SignalLedgerService.update_signal.return_value.set_result(True)

        res = await SignalLifecycleService.transition_signal("test", target)

        status = "PASS" if res == allowed else "FAIL"
        print(f"{start:<20} -> {target:<20} | Allowed: {allowed:<5} | Actual: {res:<5} | {status}")

    # Restore
    SignalLedgerService.get_signal = original_get_signal
    SignalLedgerService.update_signal = original_update_signal

if __name__ == "__main__":
    asyncio.run(test_lifecycle())
