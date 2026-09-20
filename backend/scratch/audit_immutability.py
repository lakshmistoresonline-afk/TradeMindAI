import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_ledger_service import SignalLedgerService

async def test_immutability():
    print("CLAIM: V2.3 Historical Immutability")
    print("-" * 60)

    mock_signal = MagicMock()
    mock_signal.id = "hist_1"
    mock_signal.status = "TARGET_HIT"

    mock_session = MagicMock()
    mock_session.query().filter().first.return_value = mock_signal

    # Attempt to change target_price
    res = await SignalLedgerService.update_signal("hist_1", {"target_price": 9999}, session=mock_session)

    print(f"Mutation of target_price in TARGET_HIT: {'BLOCKED' if not res else 'ALLOWED'}")

    if not res:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

if __name__ == "__main__":
    asyncio.run(test_immutability())
