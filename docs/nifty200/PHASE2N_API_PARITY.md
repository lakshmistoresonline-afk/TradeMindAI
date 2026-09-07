# PHASE 2N: API & EXPORT PARITY

## 1. Objective
Ensure that the new F&O extension fields are correctly transmitted via the `/active-signals` API.

## 2. Parity Test (F&O Contract)
- **ID**: `master_opt_SBIN_860_122636`
- **Neon Field**: `instrument_id` = `SBIN860CE`
- **API Response**: `instrument_id` = `SBIN860CE`
- **Match**: **YES**.

## 3. Serialization Proof
Pydantic model `LiveSignal` correctly serializes all Ledger 2.0 extension fields into the JSON response.

---
**Verdict**: API Parity PASS.
