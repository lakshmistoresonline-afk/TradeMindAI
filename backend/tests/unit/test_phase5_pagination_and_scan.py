import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.services.signal_eligibility import is_eligible_buy
from backend.domain.models.stock import Stock

@pytest.mark.asyncio
async def test_pagination_traversal_without_truncation():
    # Mock repository returning batches of stocks simulating pagination (> 1000 items)
    mock_repo = MagicMock()
    batch_1 = [Stock(symbol=f"SYM{i}", name=f"Stock {i}") for i in range(200)]
    batch_2 = [Stock(symbol=f"SYM{i}", name=f"Stock {i}") for i in range(200, 400)]
    batch_3 = [] # termination

    mock_repo.get_all_stocks = AsyncMock(side_effect=[batch_1, batch_2, batch_3])

    with patch('backend.services.equity_signal_generation_service.container') as mock_container:
        mock_container.repository = mock_repo
        # Mock signal generation to return None so scan runs through without actual ML calls
        with patch('backend.services.equity_signal_generation_service.SignalEngine.generate_signal', new_callable=AsyncMock, return_value=None):
            result = await EquitySignalGenerationService.run_production_scan()
            assert result["source_symbol_count"] == 400
            assert result["status"] == "COMPLETED"
            assert mock_repo.get_all_stocks.call_count == 3

@pytest.mark.asyncio
async def test_pagination_page_failure_handling():
    mock_repo = MagicMock()
    mock_repo.get_all_stocks = AsyncMock(side_effect=Exception("Database read timeout"))

    with patch('backend.services.equity_signal_generation_service.container') as mock_container:
        mock_container.repository = mock_repo
        result = await EquitySignalGenerationService.run_production_scan()
        assert result["status"] == "FAILED"
        assert "PAGINATION_FAILED" in result["reason"]

def test_centralized_buy_eligibility_strict():
    # Valid BUY
    assert is_eligible_buy({"direction": "LONG", "rating": "BUY"}) is True
    assert is_eligible_buy({"direction": "LONG", "rating": "STRONG_BUY"}) is True

    # Invalid / conflicting directions and ratings
    assert is_eligible_buy({"direction": "SHORT", "rating": "BUY"}) is False
    assert is_eligible_buy({"direction": "LONG", "rating": "SELL"}) is False
    assert is_eligible_buy({"direction": "LONG", "rating": "HOLD"}) is False
    assert is_eligible_buy({"direction": "LONG", "rating": "BUY", "signal_rating": "SELL"}) is False
    assert is_eligible_buy(None) is False
