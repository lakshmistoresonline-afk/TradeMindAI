# Nifty 500 Data Validation Report

**Generated**: 2026-11-04T03:38:44.029578+00:00
**Global Data Status**: `DEGRADED_UNSUPPORTED`
**Signal Generation Allowed**: `False`

## Summary Statistics

- **Canonical Symbol Count**: `500`
- **Accounted Symbol Count**: `500`
- **Historical Data Pass Count**: `452` / 500
- **Intraday 5m Data Pass Count**: `276` / 500
- **Storage Consistency Pass Count**: `499` / 500
- **Overall PASS Count**: `241`
- **Overall PARTIAL Count**: `258`
- **Overall FAILED Count**: `0`
- **Overall UNSUPPORTED Count**: `1`

## Per-Category Dynamic Findings

- **Storage Consistency**: `499` symbols pass DuckDB vs Parquet value-level equality check ($10^{-4}$ tolerance).
- **Unsupported/Unlisted Symbols**: `1` symbols (BAGMANE).
- **Partial/Degraded Symbols**: `258` symbols (360ONE, ABB, AIAENG, APLAPOLLO, AUBANK).
- **Signal Generation Gate**: Enforces `signal_generation_allowed = False` while any symbol is degraded or unsupported.
