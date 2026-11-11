# Nifty 500 Data Validation Report

**Generated**: 2026-11-11T03:10:31.576410+00:00
**Global Data Status**: `FAILED`
**Signal Generation Allowed**: `False`

## Summary Statistics

- **Canonical Symbol Count**: `500`
- **Accounted Symbol Count**: `500`
- **Historical Data Pass Count**: `0` / 500
- **Intraday 5m Data Pass Count**: `0` / 500
- **Storage Consistency Pass Count**: `0` / 500
- **Overall PASS Count**: `0`
- **Overall PARTIAL Count**: `0`
- **Overall FAILED Count**: `500`
- **Overall UNSUPPORTED Count**: `0`

## Per-Category Dynamic Findings

- **Storage Consistency**: `0` symbols pass DuckDB vs Parquet value-level equality check ($10^{-4}$ tolerance).
- **Unsupported/Unlisted Symbols**: `0` symbols (None).
- **Partial/Degraded Symbols**: `0` symbols (None).
- **Signal Generation Gate**: Enforces `signal_generation_allowed = False` while any symbol is degraded or unsupported.
