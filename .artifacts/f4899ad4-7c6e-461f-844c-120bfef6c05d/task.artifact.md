# Task Checklist - STEP 4: Forensic Revalidation

- `[/]` Step 1: reproduction & Extraction
    - `[x]` Create forensic script `step4_expired_forensic.py`
    - `[x]` Execute forensic script and save `docs/STEP4_EXPIRED_FORENSIC.csv`
    - `[x]` Re-run backtest to confirm exact counts (38,636 trades)
- `[/]` Step 2: Algorithmic Correction
    - `[x]` Verify short return formula in `OutcomeEngine.py` (Confirmed: Correct)
    - `[ ]` Fix `OutcomeEngine.py` to handle non-triggered expirations (set profit to 0.0)
    - `[ ]` Audit "Same-Bar Stop" policy implementation
- `[ ]` Step 3: Data Integrity Audit
    - `[ ]` Investigate ADANIPOWER/ADANIENT extreme losses (Confirmed: Phantom losses from non-entry)
    - `[ ]` Check for corporate action gaps (splits/bonus) - ADANIPOWER 15->53 confirmed as genuine market move but phantom loss.
- `[ ]` Step 4: Recalculation & Scenarios
    - `[x]` Calculate Scenario B (Exclude non-triggered trades)
    - `[ ]` Calculate Scenario C (Gap-at-Open execution + 3% hard stop)
- `[ ]` Step 5: Reporting
    - `[ ]` Generate `docs/STEP4_EXPIRED_FORENSIC_REPORT.md`
    - `[ ]` Update `docs/STEP4_CORRECTED_BASELINE_REPORT.md`
    - `[ ]` Update `docs/STEP4_CORRECTED_RESULTS.json`
