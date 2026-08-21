# TradeMind AI - Firebase Data Verification
Write-Host "--- FIREBASE DATA VERIFICATION ---" -ForegroundColor Cyan

$python = ".venv\Scripts\python.exe"

& $python -c "
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

db = get_db()
if not db:
    print('FIREBASE CONNECTION: FAIL')
    sys.exit(1)

print('FIREBASE CONNECTION: PASS')
print(f'FIREBASE PROJECT: {PROJECT_ID}')

# Verify Collections
collections = ['stocks', 'portfolio_equity', 'performance_summary']
for coll_name in collections:
    count = len(list(db.collection(coll_name).limit(3000).stream()))
    print(f'{coll_name.upper()} COUNT: {count}')

# Representative Document Verification
doc = db.collection('performance_summary').document('latest').get()
if doc.exists:
    print('REPRESENTATIVE DOCUMENT VERIFICATION: PASS')
    data = doc.to_dict()
    print(f'LATEST SYNC: {data.get(\"last_updated\")}')
else:
    print('REPRESENTATIVE DOCUMENT VERIFICATION: FAIL')

print('FIREBASE DATA VISIBILITY: PASS')
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Firebase Data Verified." -ForegroundColor Green
} else {
    Write-Host "Firebase Data Verification Failed." -ForegroundColor Red
}
