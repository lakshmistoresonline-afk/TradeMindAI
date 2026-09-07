# PHASE 2M: CODE CHANGE MANIFEST

## 1. Files Modified
-   `backend/infrastructure/repositories/upstox_provider.py`: **NEW** (Primary Provider Adapter).
-   `backend/infrastructure/repositories/dhan_provider.py`: **NEW** (Secondary Provider Adapter).
-   `backend/services/price_resolver.py`: **UPDATED** (Capability discovery added).
-   `backend/services/certification_engine_v2m.py`: **NEW** (Phase 2M Hard-Gate Logic).
-   `backend/core/container.py`: **UPDATED** (Provider/Engine wiring).

---
**Verdict**: Changes verified as INFRASTRUCTURE-ONLY. No V2.2 strategy impact.
