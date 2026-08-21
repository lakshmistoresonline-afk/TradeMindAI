import os
import sys
import pandas as pd
from sqlalchemy import func
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, ShadowScanDiagnosticDB

def generate_report():
    with SessionLocal() as session:
        latest_ts = session.query(func.max(ShadowScanDiagnosticDB.scan_timestamp)).scalar()
        if not latest_ts:
            print("[!] No diagnostic data found.")
            return

        query = session.query(ShadowScanDiagnosticDB).filter(ShadowScanDiagnosticDB.scan_timestamp == latest_ts).statement
        df = pd.read_sql(query, session.bind)

        print("\n============================================================")
        print(" SHADOW SCAN DIAGNOSTIC SUMMARY")
        print("============================================================")
        print(f"Scan Timestamp: {latest_ts}")
        print(f"Total Symbols Scanned: {len(df)}")

        signals = df[df['signal_decision'] == 'SIGNAL_GENERATED']
        print(f"Signals Passed Gates: {len(signals)}")

        print("\n[REJECTION BREAKDOWN]")
        rejections = df[df['signal_decision'] == 'REJECTED']
        if not rejections.empty:
            counts = rejections['rejection_reason'].value_counts()
            for reason, count in counts.items():
                print(f"{reason: <25}: {count}")
        else:
            print("No rejections recorded.")

        print("\n[TOP 20 SIGNAL SCORES (Diagnostic)]")
        # Ensure signal_score is numeric for sorting
        df['signal_score'] = pd.to_numeric(df['signal_score'], errors='coerce').fillna(0.0)
        top_20 = df.sort_values('signal_score', ascending=False).head(20)
        print(top_20[['symbol', 'signal_score', 'rejection_reason']].to_string(index=False))

        print("\n[DATA FRESHNESS AUDIT]")
        freshness = df['stale_data_status'].value_counts()
        for status, count in freshness.items():
            print(f"{status: <25}: {count}")

        print("============================================================")

if __name__ == "__main__":
    generate_report()
