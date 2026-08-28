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

def verify():
    db = get_db()
    if not db:
        print('FIREBASE CONNECTION: FAIL')
        sys.exit(1)

    print('FIREBASE CONNECTION: PASS')

    collections = ['shadow_signals', 'shadow_summary', 'shadow_equity', 'shadow_scan_diagnostics']
    for coll_name in collections:
        docs = list(db.collection(coll_name).limit(10).stream())
        print(f'COLLECTION {coll_name.upper()}: {"FOUND" if len(docs) > 0 else "EMPTY"} (Count: {len(docs)})')

    # Check Summary
    doc = db.collection('shadow_summary').document('latest').get()
    if doc.exists:
        print('SHADOW SUMMARY VERIFICATION: PASS')
        equity = doc.to_dict().get("equity")
        print(f'LATEST EQUITY: {equity}')
    else:
        print('SHADOW SUMMARY VERIFICATION: FAIL')

if __name__ == "__main__":
    verify()
