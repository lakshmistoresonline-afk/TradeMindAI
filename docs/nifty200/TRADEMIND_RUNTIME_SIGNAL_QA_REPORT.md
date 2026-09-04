# TRADEMIND AI: RUNTIME SIGNAL QA REPORT

## 1. Dashboard Audit
- **Shadow Monitor**: Reconciled metrics displayed correctly (WR: 58.0%, PF: 2.72).
- **Signal Detail**: All 4 tiers (Executive, Price, AI, Audit) populated correctly.
- **Population Filters**: Reconstructed, Legacy, and Verified filters active.

## 2. API Audit
- `GET /shadow/summary`: Returns reconciled metrics from `ForensicAnalyticalService`.
- `GET /shadow/signals/{id}`: Returns full Ledger 2.0 schema.
- `GET /shadow/integrity/report`: Returns pass status for temporal isolation.

## 3. Data Integrity
- **Current vs Entry**: Confirmed visually and via API that these are separate.
- **P&L Accuracy**: All verified terminal outcomes match the cost-aware P&L engine.

---
**Status**: RUNTIME_CERTIFIED
