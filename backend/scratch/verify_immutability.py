import sys
import os
from unittest.mock import MagicMock
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_ledger_service import SignalLedgerService

async def test_immutability():
    print("CLAIM: Restricted fields cannot be mutated in TERMINAL states")
    print("-" * 60)

    # 1. Mock DB Object in Terminal State
    mock_signal = MagicMock()
    mock_signal.id = "sig_1"
    mock_signal.status = "TARGET_HIT"

    # 2. Mock Session
    mock_session = MagicMock()
    mock_session.query().filter().first.return_value = mock_signal

    # 3. Try to update restricted field
    updates = {"entry_price": 500.0}

    # We call update_signal with our mock session
    res = await SignalLedgerService.update_signal("sig_1", updates, session=mock_session)

    print(f"Update entry_price in TARGET_HIT status: {'BLOCKED' if not res else 'ALLOWED'}")

    if not res:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

if __name__ == "__main__":
    asyncio.run(test_immutability())
