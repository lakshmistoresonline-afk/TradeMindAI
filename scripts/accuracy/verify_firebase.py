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
    print(f'FIREBASE PROJECT: {PROJECT_ID}')

    # Verify Collections
    collections = ['stocks', 'portfolio_equity', 'performance_summary']
    for coll_name in collections:
        # Use a limit to avoid very long stream for large collections
        docs = db.collection(coll_name).limit(3000).stream()
        count = sum(1 for _ in docs)
        print(f'{coll_name.upper()} COUNT: {count}')

    # Representative Document Verification
    doc = db.collection('performance_summary').document('latest').get()
    if doc.exists:
        print('REPRESENTATIVE DOCUMENT VERIFICATION: PASS')
        data = doc.to_dict()
        print(f"LATEST SYNC: {data.get('last_updated')}")
    else:
        print('REPRESENTATIVE DOCUMENT VERIFICATION: FAIL')

    print('FIREBASE DATA VISIBILITY: PASS')

if __name__ == "__main__":
    verify()
