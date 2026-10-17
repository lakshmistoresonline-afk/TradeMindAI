import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.services.signal_eligibility import is_eligible_buy
from backend.workers.lifecycle_worker import SignalLifecycleWorker
from backend.domain.models.stock import Stock

@pytest.mark.asyncio
async def test_pagination_stress_test_over_1201_records():
    # Mock repository returning batches of stocks simulating pagination > 1201 items (page size 200)
    mock_repo = MagicMock()
    batches = []
    total_items = 1250
    page_size = 200
    for offset in range(0, total_items, page_size):
        end = min(offset + page_size, total_items)
        batch = [Stock(symbol=f"SYM{i}", name=f"Stock {i}") for i in range(offset, end)]
        batches.append(batch)
    batches.append([]) # termination

    mock_repo.get_all_stocks = AsyncMock(side_effect=batches)

    with patch('backend.services.equity_signal_generation_service.container') as mock_container:
        mock_container.repository = mock_repo
        with patch('backend.services.equity_signal_generation_service.SignalEngine.generate_signal', new_callable=AsyncMock, return_value=None):
            result = await EquitySignalGenerationService.run_production_scan()
            assert result["source_symbol_count"] == total_items
            assert result["status"] == "COMPLETED"
            # 1250 items with page size 200 = 7 pages (0, 200, 400, 600, 800, 1000, 1200) + 1 termination call = 8 calls
            assert mock_repo.get_all_stocks.call_count == 7

@pytest.mark.asyncio
async def test_later_page_failure_fails_scan():
    mock_repo = MagicMock()
    batch_1 = [Stock(symbol=f"SYM{i}", name=f"Stock {i}") for i in range(200)]
    mock_repo.get_all_stocks = AsyncMock(side_effect=[batch_1, Exception("Later page DB read failure")])

    with patch('backend.services.equity_signal_generation_service.container') as mock_container:
        mock_container.repository = mock_repo
        result = await EquitySignalGenerationService.run_production_scan()
        assert result["status"] == "FAILED"
        assert "PAGINATION_FAILED" in result["reason"]

@pytest.mark.asyncio
async def test_lifecycle_worker_pagination_failure_provenance():
    mock_repo = MagicMock()
    mock_repo.get_all_stocks = AsyncMock(side_effect=Exception("Lifecycle storage unreachable"))

    worker = SignalLifecycleWorker()
    with patch('backend.workers.lifecycle_worker.container') as mock_container:
        mock_container.repository = mock_repo
        # Should catch exception, log, and return without raising unhandled crash
        await worker._generate_new_signals()
        assert mock_repo.get_all_stocks.call_count == 1

def test_centralized_buy_eligibility_strict_phase6():
    # Valid BUY
    assert is_eligible_buy({"direction": "LONG", "rating": "BUY"}) is True
    assert is_eligible_buy({"direction": "LONG", "signal_rating": "STRONG_BUY"}) is True

    # Invalid / conflicting directions and ratings
    assert is_eligible_buy({"direction": "SHORT", "rating": "BUY"}) is False
    assert is_eligible_buy({"direction": "LONG", "rating": "SELL"}) is False
    assert is_eligible_buy({"direction": "LONG", "signal_rating": "SHORT_SELLING"}) is False
    assert is_eligible_buy({"direction": "NEUTRAL", "rating": "BUY"}) is False
    assert is_eligible_buy(None) is False
