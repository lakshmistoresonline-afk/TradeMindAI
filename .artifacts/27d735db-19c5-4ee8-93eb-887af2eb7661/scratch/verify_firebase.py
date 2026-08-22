import os
import sys
import json
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

def verify():
    db = get_db()
    if not db:
        print("COULD NOT CONNECT TO FIRESTORE")
        return

    print(f"--- FIRESTORE AUDIT (Project: {PROJECT_ID}) ---")

    # 1. shadow_summary/latest
    doc = db.collection("shadow_summary").document("latest").get()
    if doc.exists:
        data = doc.to_dict()
        print("\n[shadow_summary/latest]")
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print("\n[shadow_summary/latest] NOT FOUND")

    # 2. Active Signals
    active_ref = db.collection("shadow_signals").where("status", "==", "ACTIVE")
    active_docs = list(active_ref.stream())
    print(f"\n[shadow_signals] ACTIVE COUNT: {len(active_docs)}")
    for doc in active_docs:
        s = doc.to_dict()
        print(f"  - {s.get('symbol')}: {s.get('direction')} @ {s.get('entry_price')}")

    # 3. SBIN Signal check
    sbin_doc = db.collection("shadow_signals").document("sig_SBIN_202608180715").get()
    if sbin_doc.exists:
        s = sbin_doc.to_dict()
        print(f"\n[SBIN Signal] sig_SBIN_202608180715")
        print(f"  status: {s.get('status')}")
        print(f"  win_rate influence: {'PASSED' if s.get('status') == 'TARGET_HIT' else 'FAILED'}")
    else:
        print(f"\n[SBIN Signal] sig_SBIN_202608180715 NOT FOUND")

    # 4. Diagnostics check
    diag_ref = db.collection("shadow_scan_diagnostics").order_by("scan_timestamp", direction=firestore.Query.DESCENDING).limit(1)
    diag_docs = list(diag_ref.stream())
    if diag_docs:
        d = diag_docs[0].to_dict()
        print(f"\n[shadow_scan_diagnostics] LATEST")
        print(f"  timestamp: {d.get('scan_timestamp')}")
        print(f"  symbols in latest batch: (Need to count symbols for same timestamp)")

    # 5. System Status (if exists)
    sys_doc = db.collection("system_status").document("latest").get()
    if sys_doc.exists:
        s = sys_doc.to_dict()
        print(f"\n[system_status/latest]")
        for k, v in s.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    verify()
