# Phase 4.3.4 Real Pipeline Call Graph Report

**Date**: 2026-11-03  
**Status**: **VERIFIED**

```mermaid
flowchart TD
    A["Stored Market Data (DuckDB analytical.duckdb / Parquet backend/data/features/)"] --> B["EquitySignalGenerationService.build_feature_vector()"]
    B --> C["SignalEngine.generate_signal() (backend/services/signal_engine.py:20)"]
    C --> D["MLService.predict_with_champion() (backend/services/ml_service.py:165)"]
    C --> E["CalibrationService.get_direction_probability() (backend/services/calibration_service.py)"]
    C --> F["RiskEngine.calculate_trade_parameters() (backend/services/risk_engine.py:30)"]
    C --> G["SignalQualityService.should_publish() (backend/services/signal_quality_service.py:45)"]
    G --> H["SignalValidatorService.validate_publication() (backend/services/signal_validator_service.py)"]
    H --> I["SignalLedgerService.persist_signal() (backend/services/signal_ledger_service.py:25)"]
    I --> J["Database Ledger (LiveSignalDB / live_signals table)"]
```

## Production Call Graph Call-Sites

- **Market Data Retrieval**: `DuckDB` (`daily_ohlcv`, `intraday_5m_ohlcv`) & `Parquet` feature files.
- **Feature Vector Builder**: `build_feature_vector()` in `backend/services/equity_signal_generation_service.py` (Line 30).
- **Master Signal Engine**: `SignalEngine.generate_signal()` in `backend/services/signal_engine.py` (Line 20).
- **ML Champion Predictions**: `MLService.predict_with_champion()` in `backend/services/ml_service.py` (Line 165).
- **Quality Gate**: `SignalQualityService.should_publish()` in `backend/services/signal_quality_service.py` (Line 45).
- **Ledger Persistence**: `SignalLedgerService.persist_signal()` in `backend/services/signal_ledger_service.py` (Line 25).
