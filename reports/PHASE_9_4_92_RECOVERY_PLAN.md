# Phase 9.4.92 Authentic Market Data Recovery Plan

## 1. Recovery Objectives

1. Purge all deterministic and synthetic rows tagged with `NIFTY500_BULK_2015` or generated `YFINANCE_AUTHENTIC` rows from `PriceDB`.
2. Backfill authentic historical market price data strictly through official provider source adapters (`yfinance` API or official NSE historical archives).
3. If authentic market data is unavailable for any constituent symbol or date range, fail closed with `BLOCKED_NO_DATA` rather than inventing price observations.
4. Regenerate audit report sets and require human release operator authorization before any database write or publication.

---

## 2. Step-by-Step Recovery Workflow (Pending Operator Authorization)

### Step 1: Pre-Recovery Database Backup & Verification
- Create an immutable backup snapshot of `backend/local_operational.db` / `trade_mind.db` prior to any recovery writes:
  `cp backend/local_operational.db backend/local_operational_pre_recovery_backup.db`
- Verify backup file SHA256 hash.

### Step 2: Quarantined & Fabricated Row Isolation
- Execute a read-only query isolating rows where `source = 'NIFTY500_BULK_2015'` or `source` contains synthetic markers.
- Quarantined rows will be deleted in bounded transactional batches (5,000 rows per transaction) with rollback safety guards.

### Step 3: Authentic Market-Data Backfill via Source Adapter
- Invoke `HistoricalBackfillService.fetch_authentic_source_bars(symbol, start_date, end_date)` using `yfinance` API for all 500 Nifty 500 equities.
- Apply strict validation:
  - $open, high, low, close > 0$, $high \ge low$, $high \ge open$, $high \ge close$, $low \le open$, $low \le close$, $volume \ge 0$.
- Record source as `YFINANCE_AUTHENTIC_FETCHED` with UTC fetch timestamp.

### Step 4: Audit Set Regeneration & Human Release Operator Review
- Run `generate_audit_csvs_isolated` on clean database.
- Run `validate_audit_csvs.py` on generated set.
- Submit report set for human release review.

---

## 3. Mandatory Human Approval Requirement

**NO DATABASE WRITES OR BACKFILL OPERATIONS MAY BE EXECUTED WITHOUT EXPLICIT WRITTEN OPERATOR AUTHORIZATION.**
