import pytest
from backend.services.signal_eligibility import is_eligible_buy

def test_is_eligible_buy_positive():
    class ValidSignal:
        direction = "LONG"
        rating = "BUY"
        signal_rating = "STRONG_BUY"

    assert is_eligible_buy(ValidSignal()) is True
    assert is_eligible_buy({"direction": "LONG", "rating": "BUY"}) is True

def test_is_eligible_buy_negative():
    # 1. None / empty
    assert is_eligible_buy(None) is False
    assert is_eligible_buy({}) is False

    # 2. Short direction
    assert is_eligible_buy({"direction": "SHORT", "rating": "BUY"}) is False

    # 3. Sell rating
    assert is_eligible_buy({"direction": "LONG", "rating": "SELL"}) is False

    # 4. Conflicting short recommendation
    assert is_eligible_buy({"direction": "LONG", "rating": "STRONG_BUY", "signal_rating": "SHORT_SELL"}) is False

    # 5. Missing rating
    assert is_eligible_buy({"direction": "LONG"}) is False
