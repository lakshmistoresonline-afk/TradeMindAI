# Phase 4.2 Remediation Changelog

**Date**: 2026-11-03  
**Status**: **COMPLETED**

## Files Modified & Created

- [scripts/run_trade_mind_signal_pipeline.py](file:///D:/TradeMindAI/scripts/run_trade_mind_signal_pipeline.py): Refactored with non-destructive upserts, Parquet dataset merging, fast DuckDB loading, and 1,500 evaluation pipeline execution.
- [backend/services/signal_quality_service.py](file:///D:/TradeMindAI/backend/services/signal_quality_service.py): Updated `should_publish()` to support high-conviction probability evaluation when model metadata is un-registered.
- [backend/infrastructure/repositories/hybrid_repository.py](file:///D:/TradeMindAI/backend/infrastructure/repositories/hybrid_repository.py): Fixed ORM mapping fallbacks for `model_version` and `quality_class`.
- [backend/services/equity_signal_generation_service.py](file:///D:/TradeMindAI/backend/services/equity_signal_generation_service.py): Added `run_pilot_scan()` and time-safe feature vector builder `build_feature_vector()`.
