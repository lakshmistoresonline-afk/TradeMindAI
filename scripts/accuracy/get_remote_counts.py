import os
import sys
import subprocess
from google.oauth2 import credentials as oauth2_credentials
from google.cloud import firestore

PROJECT_ID = 'com-webcraft-trademindai-c8f75'

def get_db():
    try:
        token = subprocess.check_output('gcloud auth print-access-token', shell=True).decode('utf-8').strip()
        creds = oauth2_credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except:
        return None

def get_counts():
    db = get_db()
    if not db:
        print("FAIL: Firebase Connection")
        return

    collections = [
        'stocks', 'live_signals', 'shadow_signals', 'market_regimes',
        'instruments', 'shadow_scan_diagnostics', 'portfolio_equity',
        'performance_summary', 'system_status'
    ]

    print("Collection | Count")
    print("--- | ---")
    for coll_name in collections:
        count = 0
        # For large collections, we might need a better way than list()
        # but for reconciliation, we need the exact number if possible.
        # list() with a limit for safety or count() if supported.
        docs = db.collection(coll_name).stream()
        count = sum(1 for _ in docs)
        print(f"{coll_name} | {count}")

    # Check for sub-collections in stocks (sample)
    stocks = db.collection('stocks').limit(5).stream()
    for s in stocks:
        prices_count = sum(1 for _ in s.reference.collection('prices').stream())
        print(f"DEBUG: stocks/{s.id}/prices | {prices_count}")

if __name__ == "__main__":
    get_counts()
