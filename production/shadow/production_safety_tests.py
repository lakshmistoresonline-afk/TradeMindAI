
import pytest
import asyncio
from datetime import datetime, timedelta
from backend.services.signal_engine import SignalEngine
from production.shadow.shadow_service import ShadowService
import unittest.mock as mock

@pytest.mark.asyncio
async def test_stale_data_rejection():
    """Verify system rejects signals if data is > 24h old."""
    mock_stock = mock.MagicMock()
    mock_stock.last_price = 1000.0
    mock_stock.avg_volume = 20000000.0

    # Feature date is 2 days ago
    stale_date = datetime.utcnow() - timedelta(days=2)
    mock_features = mock.MagicMock()
    mock_features.date = stale_date
    mock_features.features = {
        "trend_ema_cross": 1.0, "ema_200": 900.0, "sma_20": 950.0, "momentum_rsi": 0.6,
        "volatility_bb": 0.5, "volume_relative": 1.2, "smc_bullish_ob": 0.0,
        "smc_bearish_ob": 0.0, "ict_liquidity_void": 0.0, "market_volatility_z": 0.0,
        "market_cap_class": 2.0, "ATR": 20.0
    }

    with mock.patch("backend.core.container.container.repository.get_stock_by_symbol", return_value=mock_stock), \
         mock.patch("backend.core.container.container.data_platform_repo.get_features_by_range", return_value=[mock_features]), \
         mock.patch("backend.core.container.container.ml_service.predict_with_champion", return_value={"prediction": "UP", "metadata": {"calibrated_probability_up": 0.6}}), \
         mock.patch("backend.core.container.container.ios_repo.get_latest_regime", return_value=None), \
         mock.patch("production.shadow.shadow_service.ShadowService.calculate_current_drawdown", return_value=0.0):

        signal = await SignalEngine.generate_signal("RELIANCE", "EQUITY", "SWING")
        assert signal is None # Rejected due to staleness

@pytest.mark.asyncio
async def test_liquidity_rejection():
    """Verify system rejects symbols with low volume."""
    mock_stock = mock.MagicMock()
    mock_stock.last_price = 1000.0
    mock_stock.avg_volume = 1000000.0 # Below 10M gate

    mock_features = mock.MagicMock()
    mock_features.date = datetime.utcnow()
    mock_features.features = {
        "trend_ema_cross": 1.0, "ema_200": 900.0, "sma_20": 950.0, "momentum_rsi": 0.6,
        "volatility_bb": 0.5, "volume_relative": 1.2, "smc_bullish_ob": 0.0,
        "smc_bearish_ob": 0.0, "ict_liquidity_void": 0.0, "market_volatility_z": 0.0,
        "market_cap_class": 2.0, "ATR": 20.0
    }

    with mock.patch("backend.core.container.container.repository.get_stock_by_symbol", return_value=mock_stock), \
         mock.patch("backend.core.container.container.data_platform_repo.get_features_by_range", return_value=[mock_features]), \
         mock.patch("backend.core.container.container.ml_service.predict_with_champion", return_value={"prediction": "UP", "metadata": {"calibrated_probability_up": 0.6}}), \
         mock.patch("production.shadow.shadow_service.ShadowService.calculate_current_drawdown", return_value=0.0):

        signal = await SignalEngine.generate_signal("RELIANCE", "EQUITY", "SWING")
        assert signal is None # Rejected due to liquidity

@pytest.mark.asyncio
async def test_drawdown_lock():
    """Verify system stops generating signals if drawdown > 15%."""
    mock_stock = mock.MagicMock()
    mock_stock.last_price = 1000.0
    mock_stock.avg_volume = 20000000.0

    mock_features = mock.MagicMock()
    mock_features.date = datetime.utcnow()
    mock_features.features = {
        "trend_ema_cross": 1.0, "ema_200": 900.0, "sma_20": 950.0, "momentum_rsi": 0.6,
        "volatility_bb": 0.5, "volume_relative": 1.2, "smc_bullish_ob": 0.0,
        "smc_bearish_ob": 0.0, "ict_liquidity_void": 0.0, "market_volatility_z": 0.0,
        "market_cap_class": 2.0, "ATR": 20.0
    }

    with mock.patch("backend.core.container.container.repository.get_stock_by_symbol", return_value=mock_stock), \
         mock.patch("backend.core.container.container.data_platform_repo.get_features_by_range", return_value=[mock_features]), \
         mock.patch("backend.core.container.container.ml_service.predict_with_champion", return_value={"prediction": "UP", "metadata": {"calibrated_probability_up": 0.6}}), \
         mock.patch("production.shadow.shadow_service.ShadowService.calculate_current_drawdown", return_value=16.5): # Over limit

        signal = await SignalEngine.generate_signal("RELIANCE", "EQUITY", "SWING")
        assert signal is None # Rejected due to drawdown lock

def test_friction_calculation():
    """Verify EV formula uses total transaction value friction."""
    from backend.services.calibration_service import CalibrationService
    ev = CalibrationService.calculate_expected_value(0.6, 30, 30, entry_price=1000)
    assert ev == 4.0
