# DATA PROVENANCE & LINEAGE REPORT

## 1. Traceability Rules
Every market data point in TradeMind carries an immutable provenance tag:

- **LIVE_PUBLIC**: Genuine current data from NSE India.
- **REFERENCE_PUBLIC**: Secondary data from Yahoo Finance.
- **HISTORICAL**: Ingested from archived exchange records.
- **CALCULATED**: Derived locally (e.g., PCR, Max Pain).

## 2. Audit Trail
The Signal Ledger (`shadow_signals` table) persists:
- `price_source`
- `price_timestamp`
- `retrieved_at`
- `data_timestamp`

This ensures that any signal can be forensically re-verified against public exchange records.

---
**Status**: AUDIT_ACTIVE.
