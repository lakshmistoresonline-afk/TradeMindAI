
import pytest
from backend.services.signal_engine import SignalEngine
from backend.services.calibration_service import CalibrationService
import unittest.mock as mock

@pytest.mark.asyncio
async def test_trend_filter_rejects_conflict():
    # Mock stock and features
    mock_stock = mock.MagicMock()
    mock_stock.last_price = 2500

    # EMA 200 is 2400 (Bullish), so SHORT should be rejected
    mock_features = mock.MagicMock()
    mock_features.features = {"ema_200": 2400, "volatility_atr": 50}

    with mock.patch("backend.core.container.container.repository.get_stock_by_symbol", return_value=mock_stock), \
         mock.patch("backend.core.container.container.data_platform_repo.get_features_by_range", return_value=[mock_features]), \
         mock.patch("backend.core.container.container.ml_service.predict_with_champion", return_value={"prediction": "DOWN", "metadata": {"calibrated_probability_up": 0.4}}), \
         mock.patch("backend.core.container.container.ios_repo.get_latest_regime", return_value=None):

        # Test SHORT signal when Price (2500) > EMA 200 (2400)
        # Should be None (Rejected by No-Trade)
        signal = await SignalEngine.generate_signal("RELIANCE", "EQUITY", "SWING")
        assert signal is None

@pytest.mark.asyncio
async def test_calibration_restored():
    prob = CalibrationService.get_direction_probability(0.8, "LONG")
    assert prob == 0.8

    prob_short = CalibrationService.get_direction_probability(0.2, "SHORT")
    assert prob_short == 0.8
