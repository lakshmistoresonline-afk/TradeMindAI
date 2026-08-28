# ML Time-Safety & Look-Ahead Protection

**Version**: 1.0.0
**Status**: ENFORCED

## 1. Core Policy

Absolutely no look-ahead bias is permitted in the TradeMind AI prediction pipeline. At any signal timestamp **T**, features and models may only utilize information that was officially available at or before **T**.

## 2. Technical Enforcement

### Feature Engineering
The `FeatureStoreService.extract_institutional_features` function accepts an optional `timestamp`. When provided:
- Historical OHLC data is strictly sliced: `df = df[df.index <= timestamp]`.
- Indicators (EMA, RSI, ATR) are calculated only on this sliced subset.
- Any attempt to use data with a timestamp `> T` will raise a `ValueError`.

### Outcome Validation
The `OutcomeEngine` separates target evaluation from feature generation:
- It only evaluates candles where `timestamp > T_signal`.
- It uses a deterministic conservative policy for same-candle ambiguity: **Stop Hit always takes precedence over Target Hit** if both occur in the same price bar.

### Walk-Forward Pipeline
Predictions are validated chronologically. Training sets are never allowed to overlap with or contain future data relative to the validation/test window.

## 3. Data Provenance
Every signal generated includes a `provenance` block containing:
- `ingestion_timestamp`: When the raw data was fetched.
- `source_timestamp`: The latest bar used for features.
- `feature_version`: The version of the extraction logic used.

## 4. Audit Trail
The `scripts/ml/walk_forward_validation.py` script serves as the primary audit tool for verifying time-safety across the NIFTY 200 universe.
