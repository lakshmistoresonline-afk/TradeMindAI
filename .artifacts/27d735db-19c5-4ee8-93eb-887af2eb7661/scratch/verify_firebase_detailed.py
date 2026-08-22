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

def verify():
    db = get_db()
    if not db: return

    print("--- DETAILED FIRESTORE AUDIT ---")

    # Active Signals
    active_ref = db.collection("shadow_signals").where("status", "==", "ACTIVE")
    active_docs = list(active_ref.stream())
    print(f"\n[ACTIVE SIGNALS] Found {len(active_docs)}")
    for doc in active_docs:
        print(f"  ID: {doc.id}")
        print(f"  Data: {doc.to_dict()}")

    # SBIN Target Hit Record
    sbin_id = "sig_SBIN_202608180715"
    doc = db.collection("shadow_signals").document(sbin_id).get()
    if doc.exists:
        print(f"\n[{sbin_id}]")
        print(f"  Data: {doc.to_dict()}")
    else:
        print(f"\n[{sbin_id}] NOT FOUND")

    # Summary
    doc = db.collection("shadow_summary").document("latest").get()
    if doc.exists:
        print(f"\n[shadow_summary/latest]")
        print(f"  Data: {doc.to_dict()}")

if __name__ == "__main__":
    verify()
