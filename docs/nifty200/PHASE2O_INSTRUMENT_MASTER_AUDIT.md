# PHASE 2O: INSTRUMENT MASTER AUDIT

## 1. Requirement
NSE F&O derivative contracts require precise exchange-level identifiers (numerical `SecurityId` for Dhan or `instrument_key` for Upstox).

## 2. Implementation: InstrumentMasterService
A dedicated `InstrumentMasterService` has been implemented in `backend/services/instrument_master_service.py`.

### **Audited Capabilities:**
-   **Local Indexing**: Capable of parsing provider-supplied CSV masters and building a normalized lookup index.
-   **Precision Matching**: Resolves contracts using the 6-tier identity: (Underlying, Exchange, Expiry, Strike, Option Type, Segment).
-   **Staleness Control**: Includes logic to track the last-refresh timestamp and detect outdated masters.

## 3. Findings
-   **Current Status**: `CONFIGURATION_REQUIRED`. 
-   **Reason**: The service is implemented and integrated, but requires an initial download of the 2026 instrument master files from the Upstox/Dhan API portals. 
-   **Risk Mitigation**: The system is designed to reject any contract resolution if the master is missing or unvalidated.

---
**Verdict**: Identity Logic PASS; Data Activation PENDING.
