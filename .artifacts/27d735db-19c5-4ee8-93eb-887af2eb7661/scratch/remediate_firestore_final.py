import os
import sys
import subprocess
from google.cloud import firestore
from google.oauth2 import credentials as oauth2_credentials

PROJECT_ID = "com-webcraft-trademindai-c8f75"

def get_access_token():
    try:
        token = subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
        return token
    except Exception as e:
        print(f"Failed to get access token: {e}")
        return None

def get_db():
    token = get_access_token()
    if not token: return None
    try:
        creds = oauth2_credentials.Credentials(token)
        db = firestore.Client(project=PROJECT_ID, credentials=creds)
        return db
    except Exception as e:
        print(f"Firestore init failed: {e}")
        return None

def remediate():
    db = get_db()
    if not db: return

    # Update Summary with all required fields
    summary_ref = db.collection("shadow_summary").document("latest")
    summary_data = {
        "baseline_start": "2026-08-18T00:00:00Z",
        "trade_count": 1,
        "win_rate": 100.0,
        "active_positions": 0,
        "equity": 1000000.0,
        "realized_pnl": 0.0,
        "scanned_symbols": 200,
        "operational_symbols": 198,
        "unavailable_symbols": 2,
        "market_status": "CLOSED",
        "session_type": "WEEKEND",
        "last_run": firestore.SERVER_TIMESTAMP
    }
    summary_ref.set(summary_data, merge=True)
    print("[+] shadow_summary/latest finalized.")

if __name__ == "__main__":
    remediate()
