# Phase 3.2.10 Executive Forensic Report

**Date**: 2026-11-03  
**Repository**: `https://github.com/lakshmistoresonline-afk/TradeMindAI.git`  
**Branch**: `main`  
**Commit SHA**: `a97300dcd7669434be2833631803377b305d5f35`  
**Parent SHA**: `7bccfc412b1877313efcff6ffbcfc64111e8dd8b`  
**Final Verdict**: **`PARTIALLY VERIFIED — SPECIFIC DEFECTS OR DATA GAPS REMAIN`**  
**Signal Generation Allowed**: `False`

---

## 1. Executive Summary & Forensic Audit Results

An independent, read-only forensic inspection was conducted across local disk storage, DuckDB tables, 1,201 Parquet feature files, and Git blob history.

- **`analytical.duckdb` (244.51 MB)**: **100% INTACT AND READABLE IN READ-ONLY MODE**. Contains `daily_ohlcv` (1,144,547 rows across 499 symbols) and `intraday_5m_ohlcv` (37,058 rows across 498 symbols) with **0 OHLCV geometry violations** and **0 nulls in required columns**.
- **Parquet Feature Files (1,201 files)**: **100% INTACT & READABLE ON LOCAL DISK** (1,000 files in `features/` live dataset + 201 files in `backup_snapshot_r4640/` backup dataset).
- **Cross-Layer Storage Equality**: 498 listed equities pass 100% DuckDB vs Parquet primary key and element-wise OHLCV value equality ($10^{-4}$ tolerance). `ICICIPRULI` has daily match with missing 5m quote, and `BAGMANE` is unlisted (`UNSUPPORTED_PROVIDER_SYMBOL`).
- **Global Validation Gate**: Strictly closed (`signal_generation_allowed = False`) while `BAGMANE` is unlisted or datasets remain degraded.

---

## 2. Reconciled Global Gate Snapshot

```json
{
  "canonical_symbol_count": 500,
  "accounted_symbol_count": 500,
  "historical_pass_count": 452,
  "intraday_pass_count": 276,
  "storage_consistent_count": 499,
  "pass_count": 241,
  "partial_count": 258,
  "failed_count": 0,
  "unsupported_count": 1,
  "global_data_status": "DEGRADED_UNSUPPORTED",
  "signal_generation_allowed": false
}
```

---

## 3. Safety Invariants

```python
REAL_TRADING = False
LIVE_EXECUTION_ENABLED = False
BROKER_ORDER_EXECUTION_ENABLED = False
QUARANTINE_ACTIVE = True
SIGNALS_ONLY_ARCHITECTURE = True
```
