import pytest
from backend.core.config import settings, Settings
from pydantic import ValidationError

def test_real_trading_is_strictly_false():
    """
    CRITICAL SECURITY AUDIT TEST:
    Asserts that REAL_TRADING, LIVE_EXECUTION_ENABLED, and BROKER_ORDER_EXECUTION_ENABLED
    are hardcoded to False in production configuration.
    """
    assert settings.REAL_TRADING is False, "CRITICAL AUDIT FAILURE: REAL_TRADING must be False"
    assert settings.LIVE_EXECUTION_ENABLED is False, "CRITICAL AUDIT FAILURE: LIVE_EXECUTION_ENABLED must be False"
    assert settings.BROKER_ORDER_EXECUTION_ENABLED is False, "CRITICAL AUDIT FAILURE: BROKER_ORDER_EXECUTION_ENABLED must be False"

def test_real_trading_enforcement_fails_closed():
    """
    CRITICAL SECURITY AUDIT TEST:
    Asserts that any environment attempt to enable REAL_TRADING or live execution
    fails closed immediately by raising a ValidationError.
    """
    with pytest.raises(ValidationError):
        Settings(REAL_TRADING=True)

    with pytest.raises(ValidationError):
        Settings(LIVE_EXECUTION_ENABLED=True)

    with pytest.raises(ValidationError):
        Settings(BROKER_ORDER_EXECUTION_ENABLED=True)

def test_public_config_endpoint_returns_real_trading_false():
    """
    Asserts that the public configuration API route explicitly reports real_trading=False.
    """
    from backend.api.v1.endpoints.public import get_public_config
    import asyncio

    config = asyncio.run(get_public_config())
    assert config["real_trading"] is False
    assert config["universe"] == "NIFTY-200"
