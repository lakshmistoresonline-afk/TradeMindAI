# Baseline Configuration - 2026-08-17

## 1. Feature Set
*   `trend_ema_cross`: EMA 20 > EMA 50
*   `momentum_rsi`: RSI scaled 0-1
*   `volatility_bb`: Distance from Bollinger Bands
*   `volume_relative`: Relative volume vs 20d mean
*   `smc_bullish_ob`: Presence of Bullish Order Block
*   `smc_bearish_ob`: Presence of Bearish Order Block
*   `ict_liquidity_void`: Detection of price gap
*   `fii_net_bias`: Standardized FII net flow bias

## 2. Model Parameters
*   **Type**: RandomForestClassifier
*   **n_estimators**: 100
*   **random_state**: 42
*   **Split**: 60% Train, 20% Calibrate, 20% Test (Chronological)

## 3. Calibration Parameters
*   **Method**: Platt Scaling (Sigmoid transformation via Logistic Regression)
*   **Segment Baselines (Platt A/B)**:
    *   EQUITY: a=-5.0, b=0.5
    *   FUTURES: a=-4.2, b=0.3
    *   OPTIONS: a=-6.5, b=1.2

## 4. Signal Thresholds
*   `calibrated_prob` >= 0.52 (BUY/SELL)
*   `expected_val` > 0
*   `risk_pct` <= 12%
*   `regime_filter`: if HIGH_VOLATILITY, `calibrated_prob` >= 0.65
*   `data_quality_score` >= 0.6 (Implicitly assumed in latest SignalEngine)

## 5. EV Assumptions (Friction)
*   `TRANSACTION_COST_PCT`: 0.05% per leg
*   `SLIPPAGE_PCT`: 0.05% per leg
*   `Total Friction`: 0.20% per round trip (conservative estimate in `calculate_expected_value`)

## 6. Outcome Policy
*   **Holdings**: Timeframe-based (SWING = 200 bars)
*   **Same-Candle Ambiguity**: STOP LOSS assumes hit first (Conservative)
*   **Transaction Costing**: Applied to Reward/Risk in EV calculation.
