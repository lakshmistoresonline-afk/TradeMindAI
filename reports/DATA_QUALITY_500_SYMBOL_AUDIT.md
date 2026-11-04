# Data Quality 500 Symbol Audit

**Date**: 2026-11-03  
**Evaluated Universe**: 500 Canonical Nifty 500 Equities  
**Global Gate Status**: `DEGRADED_UNSUPPORTED`  
**Signal Generation Allowed**: `False`

## Executive Summary

An exhaustive, non-destructive audit was performed across all 500 canonical Nifty 500 equities.

- **Canonical Symbol Count**: `500`
- **Accounted Symbol Count**: `500`
- **Historical Data Pass Count**: `452` / 500 (48 PARTIAL due to IPO listing boundaries/holidays)
- **Intraday 5m Data Pass Count**: `276` / 500 (224 PARTIAL due to 1-2 missing 5m volume slots or provider quote limits)
- **Storage Consistency Pass Count**: `499` / 500 (`BAGMANE` unsupported unlisted equity)
- **Overall PASS Count**: `241` / 500
- **Overall PARTIAL Count**: `258` / 500
- **Overall UNSUPPORTED Count**: `1` (`BAGMANE`)
- **Signal Generation Gate**: Enforces `signal_generation_allowed = False` strictly while any symbol is degraded or unsupported.
