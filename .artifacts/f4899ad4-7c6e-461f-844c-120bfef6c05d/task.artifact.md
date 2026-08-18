# Task Checklist - Shadow Outcome Notification Automation

- `[/]` Implementation
    - `[ ]` Create `production/reports/shadow_reporter.py`
    - `[ ]` Modify `production/shadow/shadow_service.py` to automate outcome handling
    - `[ ]` Update `production/reports/generate_shadow_report.py` for integrated progress tracking
- `[ ]` Verification
    - `[ ]` Verify DB persistence of terminal outcomes
    - `[ ]` Confirm detailed outcome report generation (`SHADOW_OUTCOME_<id>.md`)
    - `[ ]` Confirm "Latest Outcome" update (`SHADOW_LATEST_OUTCOME.md`)
    - `[ ]` Verify completed trade count stability across restarts
