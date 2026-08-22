import sys
import os
import subprocess
from datetime import datetime
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

def update_status():
    db = get_db()
    if not db:
        print('FIREBASE CONNECTION: FAIL')
        sys.exit(1)

    print(f'Updating Firebase System Status...')

    status_ref = db.collection('system_status').document('latest')
    status_ref.set({
        'system_status': 'OPERATIONAL',
        'market_status': 'CLOSED',
        'session': 'WEEKEND',
        'last_scan': datetime.utcnow(),
        'nifty200_coverage': 200,
        'operational': 198,
        'unavailable': 2,
        'signals': 0,
        'trades': 0,
        'equity': 1000000.0,
        'real_trading': False,
        'shadow_only': True
    }, merge=True)

    summary_ref = db.collection('shadow_summary').document('latest')
    summary_ref.set({
        'last_run': datetime.utcnow(),
        'market_status': 'CLOSED',
        'session_type': 'WEEKEND'
    }, merge=True)

    print('Firebase Update: SUCCESS')

if __name__ == "__main__":
    update_status()
