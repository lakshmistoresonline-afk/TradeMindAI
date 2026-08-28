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

    print(f'--- FIREBASE COMPLETE DATA VERIFICATION: {PROJECT_ID} ---')

    collections = [
        'stocks', 'market_regimes', 'live_signals', 'shadow_signals',
        'shadow_scan_diagnostics', 'portfolio_equity', 'performance_summary',
        'system_status'
    ]

    for coll in collections:
        docs = list(db.collection(coll).limit(10).stream())
        print(f'{coll.upper(): <25}: FOUND ({len(docs) if len(docs) < 10 else "10+"} docs)')

    # Check specific critical summaries
    print("\n[CRITICAL DATA CHECK]")
    summary_ref = db.collection('performance_summary')
    for doc_id in ['backtest', 'walk_forward']:
        doc = summary_ref.document(doc_id).get()
        if doc.exists:
            print(f"   {doc_id.upper()} SUMMARY: PASS (Return: {doc.to_dict().get('total_return')}%)")
        else:
            print(f"   {doc_id.upper()} SUMMARY: FAIL")

    status_doc = db.collection('system_status').document('latest').get()
    if status_doc.exists:
        print(f"   SYSTEM STATUS: {status_doc.to_dict().get('system_status') or 'OPERATIONAL'}")

if __name__ == "__main__":
    verify()
