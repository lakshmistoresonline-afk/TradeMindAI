# TradeMindAI — Phase 5.18 Strategy V2.2 Frozen File Integrity Report

## 1. SHA-256 Hash Comparison Matrix

| Frozen File | Relative Path | 2026-09-11 Manifest SHA-256 | Git HEAD Blob SHA-256 | Current Working-Tree SHA-256 | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `signal_engine` | `backend/services/signal_engine.py` | `90E4B640A855...` | `21162CED04BD59BB47EAD53DDFD1971520C67CA1980FC9EAE07929312C2E9228` | `21162CED04BD59BB47EAD53DDFD1971520C67CA1980FC9EAE07929312C2E9228` | **MATCH_HEAD** |
| `outcome_engine` | `backend/services/outcome_engine.py` | `460F8567D406...` | `65E2CB6D8E561B55855F7920513172EC7E69639CD53E8A8794DDECCD46980C98` | `65E2CB6D8E561B55855F7920513172EC7E69639CD53E8A8794DDECCD46980C98` | **MATCH_HEAD** |
| `risk_engine_service` | `backend/services/risk_engine.py` | `BE1DC856903B...` | `D3169C30552D6DDAB245A87442BA213126EBB2A66F4558B9109E363BC540BAEF` | `D3169C30552D6DDAB245A87442BA213126EBB2A66F4558B9109E363BC540BAEF` | **MATCH_HEAD** |
| `risk_core` | `backend/core/risk.py` | `9910889561C6...` | `9910889561C6A941E7D011EF6EF53A28285F7CF7FDE4CE4BDEECBD27003CB830` | `9910889561C6A941E7D011EF6EF53A28285F7CF7FDE4CE4BDEECBD27003CB830` | **MATCH_HEAD_AND_MANIFEST** |
| `configuration` | `backend/core/config.py` | `92EDE1FCD919...` | `3C671487E46F365D78A778D049B11CB6B45B654FDF8A92B607F379508AC83EA6` | `0EB91555EA9FC40F3F2C614260F6C701671F5BB2A193ED6A69333CA60E16B353` | **AUTHORIZED_PATCH** |

---

## 2. Integrity Analysis & Honest Status

- **Working-Tree Byte Integrity**: Current working-tree strategy files match committed Git HEAD blobs **100%** byte-for-byte.
- **Authorized Config Patch**: `backend/core/config.py` contains authorized 1-line addition `SIGNALS_ONLY_ARCHITECTURE: bool = True`.
- **Historical Provenance Note**: `risk.py` matches the 2026-09-11 manifest hash **100%**. `signal_engine.py`, `outcome_engine.py`, `risk_engine.py`, and `config.py` reflect pre-HEAD baseline commits, yielding `PARTIAL — HISTORICAL BASELINE RECONCILIATION REQUIRED` for historical provenance while current HEAD integrity is 100% verified.
