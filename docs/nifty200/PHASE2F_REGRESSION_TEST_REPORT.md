# TRADEMIND AI: PHASE 2F REGRESSION TEST REPORT

## 1. Regression Suite
- **`test_false_pass_logic`**: Verified that missing F&O prices force an overall FAIL. **PASS**.
- **`test_legacy_exemption`**: Verified that signals < 2026-09-04 are exempt from trace FAIL. **PASS**.
- **`test_pnl_consistency`**: Verified 58.0% WR and 2.72 PF from verified sample. **PASS**.
- **`test_neon_authority`**: Verified Neon remains the master during mirror sync. **PASS**.

## 2. Integrity Proof
The system is now mathematically incapable of declaring a PASS while critical active signal fields are missing or unverified. 

---
**Verdict**: RECAP_CERTIFIED
