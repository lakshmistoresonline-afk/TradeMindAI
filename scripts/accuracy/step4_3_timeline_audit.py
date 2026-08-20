import json
import pandas as pd
import os
from datetime import datetime

def run_timeline_audit():
    results_path = 'data/results/portfolio_trades.csv'
    if not os.path.exists(results_path):
        print("Portfolio trades ledger missing. Run portfolio_simulator first.")
        return

    df = pd.read_csv(results_path)

    # 1. Chronology Verification
    # signal_date <= entry_date <= exit_date
    df['signal_dt'] = pd.to_datetime(df['signal_date'])
    df['entry_dt'] = pd.to_datetime(df['entry_date'])
    df['exit_dt'] = pd.to_datetime(df['exit_date'])

    violations = df[~((df['signal_dt'] <= df['entry_dt']) & (df['entry_dt'] <= df['exit_dt']))]

    # 2. Date Range
    min_date = df['signal_dt'].min()
    max_date = df['exit_dt'].max()

    audit_md = f"""# TradeMind AI - Step 4.3 Timeline Audit

## Chronological Overview
- **Earliest Signal**: {min_date.isoformat()}
- **Latest Exit**: {max_date.isoformat()}
- **Total Trade Observation Period**: {(max_date - min_date).days} days

## Strict Chronology Assertions
- `signal_date <= entry_date`: {"PASS" if (df['signal_dt'] <= df['entry_dt']).all() else "FAIL"}
- `entry_date <= exit_date`: {"PASS" if (df['entry_dt'] <= df['exit_dt']).all() else "FAIL"}

## Violations Found
- **Count**: {len(violations)}
"""
    if len(violations) > 0:
        audit_md += "\n### Sample Violations\n" + violations.head(5).to_markdown()

    with open('docs/step4_3/TIMELINE_AUDIT.md', 'w') as f:
        f.write(audit_md)
    print("Generated docs/step4_3/TIMELINE_AUDIT.md")

if __name__ == "__main__":
    run_timeline_audit()
