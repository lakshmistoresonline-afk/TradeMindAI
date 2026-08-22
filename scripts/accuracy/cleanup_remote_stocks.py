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

def cleanup():
    db = get_db()
    if not db:
        print("FAIL: Firebase Connection")
        return

    # Extra symbols identified in reconcile_stocks.py
    extra = ['L&T', 'AU SMALL FINANCE BANK', 'SBI']

    print(f"[*] Cleaning up {len(extra)} extra documents in 'stocks' collection...")
    for sym in extra:
        try:
            db.collection('stocks').document(sym).delete()
            print(f"   [-] Deleted {sym}")
        except Exception as e:
            print(f"   [!] Error deleting {sym}: {e}")

    print("[SUCCESS] Remote stock master normalized.")

if __name__ == "__main__":
    cleanup()
