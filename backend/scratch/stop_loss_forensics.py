import os
import sys
import json
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

# Load environment
os.environ["ENVIRONMENT"] = "production"
os.environ["SECRET_KEY"] = "A" * 32
os.environ["MARKET_DATA_INGEST_KEY"] = "SECURE_INGEST_KEY_2026"
os.environ["POSTGRES_URL"] = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

from backend.core.postgres import SessionLocal

def run_forensics():
    db = SessionLocal()
    try:
        query = text("""
            SELECT * FROM shadow_signals WHERE status = 'STOP_LOSS'
            UNION ALL
            SELECT * FROM live_signals WHERE status = 'STOP_LOSS'
        """)
        res = db.execute(query)
        columns = res.keys()
        sl_signals = [dict(zip(columns, row)) for row in res.fetchall()]

        print(f"[*] Analyzing {len(sl_signals)} STOP_LOSS signals...")

        forensic_records = []
        for s in sl_signals:
            entry = s.get("entry_price") or 0.0
            stop = s.get("stop_price") or 0.0
            target = s.get("target_price") or 0.0

            stop_dist = abs(entry - stop) / entry * 100 if entry > 0 else 0
            target_dist = abs(target - entry) / entry * 100 if entry > 0 else 0
            rr = target_dist / stop_dist if stop_dist > 0 else 0

            mae = s.get("realized_mae") or 0.0
            mfe = s.get("realized_mfe") or 0.0

            # Classification Logic
            failure_class = "UNKNOWN"
            if mfe < 0.2:
                failure_class = "IMMEDIATE_FAILURE"
            elif mfe > target_dist * 0.8:
                failure_class = "NEAR_TARGET_REVERSAL"
            elif mfe > stop_dist:
                failure_class = "LATE_REVERSAL"
            elif mae < stop_dist * 1.1:
                failure_class = "EARLY_NOISE_STOP"
            else:
                failure_class = "DIRECTIONAL_FAILURE"

            record = {
                "signal_id": s.get("id"),
                "symbol": s.get("symbol"),
                "direction": s.get("direction"),
                "timestamp": s.get("timestamp"),
                "entry": entry,
                "stop": stop,
                "target": target,
                "stop_dist_pct": round(stop_dist, 2),
                "target_dist_pct": round(target_dist, 2),
                "rr": round(rr, 2),
                "conviction": s.get("conviction") or s.get("ai_investment_score"),
                "prob": s.get("calibrated_probability"),
                "regime": s.get("regime"),
                "vix": s.get("vix") or 0.0,
                "mae": round(mae, 2),
                "mfe": round(mfe, 2),
                "failure_classification": failure_class
            }
            forensic_records.append(record)

        df = pd.DataFrame(forensic_records)
        df.to_csv("reports/STOP_LOSS_SIGNAL_FORENSICS.csv", index=False)
        print("[+] Forensic CSV saved.")

        # Summary for MD report
        summary = df['failure_classification'].value_counts()
        print("\nFailure Classification Summary:")
        print(summary)

        # Create MD report
        with open("reports/STOP_LOSS_SIGNAL_FORENSICS.md", "w") as f:
            f.write("# Stop-Loss Signal Forensics\n\n")
            f.write("## Executive Summary\n")
            f.write(f"Analyzed {len(sl_signals)} STOP_LOSS signals from the V2.2 population.\n\n")
            f.write("### Failure Mechanism Distribution\n")
            f.write(summary.to_markdown())
            f.write("\n\n### Detailed Forensic Table\n")
            f.write(df.to_markdown(index=False))

        print("[+] Forensic Markdown report saved.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_forensics()
