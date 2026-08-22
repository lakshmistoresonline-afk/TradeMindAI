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

def inspect():
    db = get_db()
    if not db: return

    print("--- FIREBASE SAMPLE INSPECTION ---")

    # 1. Equity Samples
    print("\n[Equity Samples]")
    docs = db.collection('portfolio_equity').limit(5).stream()
    for d in docs:
        print(f"ID: {d.id} | Data: {d.to_dict()}")

    # 2. Diagnostic Samples
    print("\n[Diagnostic Samples]")
    docs = db.collection('shadow_scan_diagnostics').limit(5).stream()
    for d in docs:
        print(f"ID: {d.id} | Data: {d.to_dict()}")

if __name__ == "__main__":
    inspect()
