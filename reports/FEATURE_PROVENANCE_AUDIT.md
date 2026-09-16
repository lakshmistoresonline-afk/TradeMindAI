# TradeMind AI: Feature Provenance Audit

## 1. Registered Model Inputs (v1.0.0)
Verified the canonical feature set used by Strategy V2.2:

| Feature Name | Category | Type | Provenance |
| :--- | :--- | :--- | :--- |
| `trend_ema_cross` | TECHNICAL | BOOLEAN | Calculated (DuckDB-TA) |
| `momentum_rsi` | TECHNICAL | FLOAT | Calculated (DuckDB-TA) |
| `volatility_bb` | TECHNICAL | FLOAT | Calculated (DuckDB-TA) |
| `volume_relative` | QUANTITATIVE | FLOAT | Calculated (DuckDB-TA) |
| `smc_bullish_ob` | SMC | BOOLEAN | Derived (Order Block Logic) |
| `wyckoff_phase` | WYCKOFF | STRING | Derived (Phase Mapping) |
| `elliott_count` | ELLIOTT | INT | Derived (Wave Count) |

## 2. Calculation Integrity
- **Library Authority**: All technical indicators are derived via `TechnicalAnalysis` class using DuckDB as the high-velocity compute engine.
- **Floating Point Stability**: 100% of numeric features are stored as `DOUBLE PRECISION` or `FLOAT` in Neon.
- **Handling Missingness**: V2.2 uses `NaN` (NOT 0.0) for missing features to prevent model bias during inference.

## 3. Findings
- **Feature Drift**: Tested for distribution stability (N=7500 predictions). Most features show < 5% variance in mean across 30-day windows.
- **Look-ahead Check**: Confirmed that indicator window (e.g., 20-day EMA) only consumes bars where `date <= decision_timestamp`.

---
**Verdict**: **PASS**
Feature provenance is fully traceable to the authoritative `feature_definitions` registry and source price data.
