import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DATABASE_URL = os.getenv("POSTGRES_URL")

def main():
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM live_signals;"))
        signals = [dict(r._mapping) for r in res.fetchall()]
        print(f"Auditing {len(signals)} signals...")

    audit_results = []

    for s in signals:
        issues = []

        # 1. Basic Fields
        if not s.get('entry_price'): issues.append("MISSING_ENTRY")
        if not s.get('target_price'): issues.append("MISSING_TARGET")
        if not s.get('stop_price'): issues.append("MISSING_STOP")

        # 2. R:R Recalculation
        entry = s.get('entry_price', 0)
        target = s.get('target_price', 0)
        stop = s.get('stop_price', 0)

        if entry and target and stop:
            if s['direction'] == 'LONG':
                reward = target - entry
                risk = entry - stop
            else:
                reward = entry - target
                risk = stop - entry

            recalc_rr = round(reward / risk, 2) if risk != 0 else 0
            stored_rr = round(s.get('risk_reward_ratio', 0), 2)

            if abs(recalc_rr - stored_rr) > 0.05:
                issues.append(f"RR_MISMATCH (Stored: {stored_rr}, Recalc: {recalc_rr})")

        # 3. Lineage
        if not s.get('prediction_id'): issues.append("MISSING_PREDICTION_ID")
        if not s.get('model_id'): issues.append("MISSING_MODEL_ID")
        if not s.get('feature_snapshot_id'): issues.append("MISSING_FEATURE_SNAPSHOT_ID")

        # 4. Temporal
        decision_ts = s.get('decision_timestamp')
        created_at = s.get('created_at')
        if decision_ts and created_at:
            if decision_ts > created_at:
                issues.append("FUTURE_DECISION_TIMESTAMP")

        audit_results.append({
            "id": s['id'],
            "symbol": s['symbol'],
            "issues": "|".join(issues) if issues else "PASS",
            "status": s['status']
        })

    df = pd.DataFrame(audit_results)
    df.to_csv("reports/CURRENT_EQUITY_SIGNAL_AUTHORITY.csv", index=False)
    print(f"Exported audit: reports/CURRENT_EQUITY_SIGNAL_AUTHORITY.csv")
    print(f"Passed: {len(df[df.issues == 'PASS'])}")
    print(f"Failed: {len(df[df.issues != 'PASS'])}")
    if len(df[df.issues != 'PASS']) > 0:
        print(df[df.issues != 'PASS'])

if __name__ == "__main__":
    main()
