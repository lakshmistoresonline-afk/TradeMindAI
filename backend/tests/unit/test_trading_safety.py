import pytest
from backend.core.trading_safety import trading_safety, Operation, TradingSafetyViolation

def test_trading_safety_allows_read_and_generate():
    trading_safety.authorize(Operation.GENERATE_SIGNAL)
    trading_safety.authorize(Operation.READ_SIGNAL)
    trading_safety.authorize(Operation.VALIDATE_SIGNAL)
    trading_safety.authorize(Operation.PUBLISH_SIGNAL)

def test_trading_safety_blocks_execution():
    with pytest.raises(TradingSafetyViolation):
        trading_safety.authorize(Operation.EXECUTE_ORDER)
    with pytest.raises(TradingSafetyViolation):
        trading_safety.execute_order(symbol="RELIANCE", qty=10)

def test_trading_safety_real_trading_false_enforced():
    with pytest.raises(TradingSafetyViolation):
        from backend.core.trading_safety import TradingSafetyPolicy
        TradingSafetyPolicy(real_trading_enabled=True)
