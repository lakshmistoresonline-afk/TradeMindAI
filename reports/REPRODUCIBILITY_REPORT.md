# TradeMind AI: Reproducibility Report

## 1. Traceability Status
Analyzed the availability of bitwise identity evidence for Strategy V2.2:

| Component | Status | Population Coverage |
| :--- | :--- | :--- |
| **Input Hashing** | **DATA_LIMITED** | 0% of historical population |
| **Decision Hashing** | **DATA_LIMITED** | 0% of historical population |
| **Prediction Linkage** | **VERIFIED** | 100% of signals linked to IDs |
| **Audit Status** | **UNVERIFIED** | (Missing Provenance Records) |

## 2. Findings
- **Legacy Artifacts**: The 50 historical signals were generated before the `shadow_provenance` identity system was implemented. While they have valid Signal and Prediction IDs, the underlying bitwise hashes (input/output) are missing.
- **Procedural Consistency**: Re-running V2.2 logic on current active signals (N=33) demonstrates procedural consistency, but bitwise proof for historical outcomes is currently unavailable.

## 3. Required Action
- Implement "Forensic Reconstruction" to backfill hashes for the 50 historical records using the archived price data.
- Ensure all *future* signals capture bitwise provenance at the moment of emission.

---
**Verdict**: **DATA_LIMITED**
Bitwise reproducibility is not established for the historical dataset due to missing provenance metadata.
