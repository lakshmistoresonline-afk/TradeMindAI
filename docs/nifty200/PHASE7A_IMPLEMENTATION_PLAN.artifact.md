# Phase 7A: Production Architecture Implementation

This phase hardens the TradeMind AI architecture for production scale, ensuring data integrity, traceability, and robust accounting parallel to Phase 6 validation.

## Authoritative Hierarchy
- **Neon (Postgres)**: Master Record of Truth.
- **Business Logic**: Canonical Domain Services.
- **Firestore**: Mirror for low-latency dashboard access.

## Proposed Changes

### 1. Database Schema Hardening (Workstreams 1, 4, 6, 9)
Update `backend/core/postgres.py` to include:
- **Universe Registry**: Explicit tracking of data freshness and blockage reasons.
- **Canonical Signals**: Unified schema for Live and Shadow signals.
- **Prediction Ledger**: Persistent storage of every model inference.
- **Model Registry**: Formal champion/challenger tracking with metrics.

### 2. Core Service Refactoring (Workstreams 4, 5, 6, 12)
- **SignalEngine**: Modify to persist a `Prediction` record before generating a `Signal`.
- **AuditService**: New service to record every state transition (INGESTED -> ANALYZED -> SIGNALED).
- **Provenance**: Snapshot all inputs (features, regime, sentiment) into the `Prediction` record.

### 3. F&O Contract Management (Workstream 3)
- Implement `ContractRegistry` to distinguish between Eligible, Discovered, and Priced contracts.
- Automated expiry handling and next-contract promotion.

### 4. Virtual Portfolio & Risk (Workstreams 7, 8)
- Harden `ShadowPortfolioEngine` to support equity curves, drawdown tracking, and sector concentration limits.
- Ensure 0.20% friction is applied at the engine level.

### 5. Data Quality Layer (Workstream 11)
- Centralized `DataQualityService` to intercept and flag invalid OHLC, future-dated candles, and stale prices.

## Implementation Steps
1.  **Schema Migration**: Idempotent SQL updates to Neon.
2.  **Model Registry & Prediction Persistence**: Link ML inference to the database.
3.  **Unified Signal Ledger**: Align `LiveSignalDB` and `ShadowSignalDB`.
4.  **Portfolio Engine Hardening**: Real-time exposure and drawdown visibility.
5.  **Audit Trail Integration**: Wrap lifecycle transitions in event logging.

## Verification Plan
- **Automated Tests**: unit tests for P&L math, lifecycle state machine, and data quality flags.
- **Reconciliation Audit**: `RECONCILE_MASTER.py` to verify Neon-Firestore-CSV parity.
- **Dashboard Scan**: Verify new production fields (MAE/MFE, Prediction ID) appear in the UI.

> [!IMPORTANT]
> **Strategy V2.2 is FROZEN.** No logic changes to entry/exit will be made.
