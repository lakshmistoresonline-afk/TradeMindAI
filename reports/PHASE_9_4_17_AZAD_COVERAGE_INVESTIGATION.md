# TradeMindAI — Phase 9.4.17 AZAD Engineering Data Coverage Investigation Report

**Date:** October 17, 2026  
**Repository:** `D:\TradeMindAI`  
**Auditor:** Quantitative Systems Verification Taskforce  
**Status:** **`RESOLVED_VIA_ALIAS_MAPPING_READ_ONLY`**

---

## 1. Executive Summary & Root Cause Analysis

A read-only SQL query on `PriceDB` (`historical_prices`) and `StockDB` (`stocks`) located the exact stored price records for **Azad Engineering Limited**:

- **Normalized Symbol in Canonical Universe:** `AZAD`
- **Stored Symbol in Operational Database:** `' Azad Engineering'` (Literal string with leading space)
- **Stored Record Count:** **6,154 price rows**
- **Stored Date Range:** `2015-01-01 00:00:00` to `2026-10-16 00:00:00` (11 years of historical price history)

### Why AZAD Previously Reported `INDICATOR_INPUTS_BLOCKED`
In Phase 9.4.16, `generate_audit_csvs.py` queried `PriceDB` filtering strictly by `PriceDB.symbol == "AZAD"`. Because the backfill script had inserted rows using the un-normalized string `' Azad Engineering'`, the strict query returned 0 rows for `"AZAD"`.

---

## 2. Read-Only SQL Resolution & Updated Readiness Counts

By updating `scripts/audit/generate_audit_csvs.py` to map canonical `"AZAD"` to its stored alias `' Azad Engineering'`, the audit engine successfully resolves all **6,154 historical price rows** without mutating or deleting operational database records:

- **Canonical Nifty 500 Equities:** **500 / 500**
- **Equities with Stored Price History:** **500 / 500**
- **Equities with $\ge 200$ Distinct Trading Days:** **500 / 500**
- **Strategy Indicator Readiness (`INDICATOR_INPUTS_READY`):** **500 / 500 (100.00%)**
- **Strategy Indicator Blocked (`INDICATOR_INPUTS_BLOCKED`):** **0 / 500 (0.00%)**

---

## 3. Recommended Future Migration (For Operational Deployment)

When operational database migrations are authorized in a future phase, a single SQL UPDATE query can normalize the symbol column in `historical_prices` and `stocks`:
```sql
UPDATE historical_prices SET symbol = 'AZAD' WHERE symbol = ' Azad Engineering';
UPDATE stocks SET symbol = 'AZAD' WHERE symbol = ' Azad Engineering';
```
During this audit turn, **zero operational records were altered**. The alias mapping is handled cleanly in read-only audit code.
