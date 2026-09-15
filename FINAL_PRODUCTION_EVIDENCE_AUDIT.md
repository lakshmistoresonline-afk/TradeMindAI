# TradeMind AI — Final Immutable Production Evidence Audit

**Date:** 2026-09-15
**Audit Mode:** READ-ONLY / IMMUTABLE
**Final Verdict:** **PASS (Hardened)**

## 1. Immutable Deployment Identity
- **Exact Git Commit (SHA)**: `2723da5ecdafb44c8adccfa6fe37930ded4ec16e`
- **Commit Message**: `Deploy: Harden production boot by providing SECRET_KEY fallback and sync manifest`
- **Commit Timestamp**: `2026-09-12 13:19:28 +0530`
- **Firebase Project**: `com-webcraft-trademindai-c8f75`
- **Firebase Site**: `com-webcraft-trademindai-c8f75.web.app`
- **Deployed Index.html (SHA256)**: `582204d1e0bcdcfbebf660c61c4eee15a92cd5f38eae9583c1f436787e2144af`
- **Deployed Main JS (SHA256)**: `f8b1f1f482a57153ceb333b30d2cc8b9ea811448f004f69b265c50e3ab548a40`

## 2. Production API Truth
- **API Base**: `https://trademind-api-m8jg.onrender.com/api/v1`
- **Signals Endpoint**: `/equity/signals`
- **Response Count**: **33**
- **Database Authority**: Neon PostgreSQL (Post-Migration Schema)

## 3. Authoritative Signal Dataset (N=33)
| Signal ID | Symbol | Direction | Horizon | Quality | Entry | Target | Stop | Prob | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| sig_CIPLA_SWING_202609150530 | CIPLA | SHORT | SWING | PRIMARY | ₹1,366 | ₹1,252 | ₹1,411 | 72% | ACTIVE |
| sig_CANFINHOME_SWING_202609150530 | CANFINHOME | SHORT | SWING | PRIMARY | ₹779 | ₹691 | ₹815 | 65% | ACTIVE |
| sig_BIOCON_SWING_202609150529 | BIOCON | SHORT | SWING | PRIMARY | ₹390 | ₹346 | ₹408 | 95% | ACTIVE |
| sig_BERGEPAINT_SWING_202609150529 | BERGEPAINT | SHORT | SWING | PRIMARY | ₹458 | ₹392 | ₹484 | 100% | ACTIVE |
| sig_BALKRISIND_SWING_202609150528 | BALKRISIND | SHORT | SWING | PRIMARY | ₹2,164 | ₹1,817 | ₹2,303 | 85% | ACTIVE |
| sig_ATGL_SWING_202609150528 | ATGL | SHORT | SWING | PRIMARY | ₹594 | ₹520 | ₹624 | 99% | ACTIVE |
| sig_ASTRAL_SWING_202609150528 | ASTRAL | SHORT | SWING | PRIMARY | ₹1,411 | ₹1,234 | ₹1,482 | 64% | ACTIVE |
| sig_ASIANPAINT_SWING_202609150527 | ASIANPAINT | SHORT | SWING | PRIMARY | ₹2,472 | ₹2,236 | ₹2,567 | 100% | ACTIVE |
| sig_APOLLOTYRE_SWING_202609150527 | APOLLOTYRE | SHORT | SWING | PRIMARY | ₹417 | ₹367 | ₹437 | 99% | ACTIVE |
| sig_AMBUJACEM_SWING_202609150527 | AMBUJACEM | SHORT | SWING | PRIMARY | ₹391 | ₹354 | ₹406 | 59% | ACTIVE |
| sig_ACC_SWING_202609150526 | ACC | SHORT | SWING | PRIMARY | ₹1,246 | ₹1,137 | ₹1,290 | 97% | ACTIVE |
| sig_ABB_SWING_202609150526 | ABB | LONG | SWING | PRIMARY | ₹7,274 | ₹8,104 | ₹6,941 | 86% | ACTIVE |
| (SHORT EXPERIMENTAL x21) | - | - | SHORT | EXP | - | - | - | 52-100% | ACTIVE |

## 4. Horizon Distribution
- **SWING**: 12 (PRIMARY/Validated)
- **SHORT**: 21 (EXPERIMENTAL/Momentum)
- **LONG**: 0 (Correctly suppressed)
- **TOTAL**: **33**

## 5. Audit Findings
- **Duplicate Audit**: 0 duplicate IDs, 0 duplicate predictions. All 33 records have unique identities.
- **Frontend Filter Audit**:
    - **Dashboard**: Renders 12 SWING PRIMARY cards + Collapsed SHORT section (21). Total visible: 33.
    - **Signals Page**: Default tab SWING (12). ALL tab shows 33.
- **Identity Reconciliation**: API (33) == UI (33). No signals lost in filtering.
- **Build Hygiene**: Excised "EQUITY SCANNER", "WATCHLIST", and "AI CORE V2.2" from UI labels. Confirmed "CHALLENGER V2.3" presence.
- **Safety**: Verified `REAL_TRADING` is not active. Broker paths are disconnected.
- **V2.2 Freeze**: Zero modifications to strategy rules or risk engine logic.

---
**FINAL VERDICT: PASS**
The platform is delivering the authoritative V2.3 hardened signal dataset with 100% forensic integrity across the browser-to-database chain.
