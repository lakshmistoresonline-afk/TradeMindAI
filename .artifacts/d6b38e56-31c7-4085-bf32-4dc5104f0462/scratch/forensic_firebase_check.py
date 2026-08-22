import os
import sys
import subprocess
import json
from google.oauth2 import credentials as oauth2_credentials
from google.cloud import firestore

PROJECT_ID = 'com-webcraft-trademindai-c8f75'

def get_db():
    try:
        token = subprocess.check_output('gcloud auth print-access-token', shell=True).decode('utf-8').strip()
        creds = oauth2_credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def check():
    db = get_db()
    if not db:
        print("Failed to connect to Firestore.")
        return

    print("--- FORENSIC FIREBASE CHECK ---")

    # 1. Check shadow_summary/latest
    summary = db.collection('shadow_summary').document('latest').get()
    if summary.exists:
        data = summary.to_dict()
        print(f"Summary Found:")
        print(f"  baseline_start: {data.get('baseline_start')}")
        print(f"  last_run: {data.get('last_run')}")
        print(f"  active_positions: {data.get('active_positions')}")
        print(f"  trade_count: {data.get('trade_count')}")
        print(f"  equity: {data.get('equity')}")
    else:
        print("Summary Not Found.")

    # 2. Check for ACTIVE shadow_signals
    active_signals = db.collection('shadow_signals').where('status', '==', 'ACTIVE').stream()
    active_list = list(active_signals)
    print(f"Active Signals in Firestore: {len(active_list)}")
    for s in active_list:
        d = s.to_dict()
        print(f"  - {d.get('symbol')} ({s.id}): Status={d.get('status')}, Direction={d.get('direction')}")

    # 3. Specifically check for SBIN
    sbin_sigs = db.collection('shadow_signals').where('symbol', '==', 'SBIN').stream()
    print("SBIN Signals Trace:")
    for s in sbin_sigs:
        d = s.to_dict()
        print(f"  - ID: {s.id}")
        print(f"    Status: {d.get('status')}")
        print(f"    Direction: {d.get('direction')}")
        print(f"    Timestamp: {d.get('timestamp')}")

if __name__ == "__main__":
    check()
