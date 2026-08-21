# Step 4.5.3 NIFTY 200 Data + Feature Pipeline Remediation Tasks

- `[x]` Phase 1: Market Calendar & Data Audit
    - `[x]` Refactor `IndianMarketCalendar` in `backend/services/market_calendar.py`
    - `[x]` Create `INVALID_SYMBOL_AUDIT.md` in `docs/step4_5/`
- `[x]` Phase 2: Data Remediation & Backfill
    - `[x]` Correct ticker mappings in `YFinanceProvider` (TMCV, PIRAMALFIN, ETERNAL)
    - `[x]` Develop `remediate_data.py` with robust backfill and target labeling
    - `[x]` Regenerate features for all 200 symbols (198 SUCCESS)
- `[x]` Phase 3: Model Training & Diagnostics
    - `[x]` Train champion models for `PEL`, `TATAMOTORS`, etc.
    - `[x]` Capture top diagnostic signal scores (PEL: 0.96)
- `[x]` Phase 4: Automation & Testing
    - `[x]` Create `STEP4_5_3_REMEDIATE_DATA.ps1`
    - `[x]` Implement regression tests in `tests/`
    - `[x]` Synchronize remediated status to Firebase
