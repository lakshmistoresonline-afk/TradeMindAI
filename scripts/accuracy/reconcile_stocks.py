import os
import sys
import sqlite3
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

def reconcile():
    db = get_db()
    if not db:
        print("FAIL: Firebase Connection")
        return

    conn = sqlite3.connect('backend/local_operational.db')
    local_stocks = set(r[0] for r in conn.execute("SELECT symbol FROM stocks").fetchall())
    conn.close()

    remote_stocks = set(d.id for d in db.collection('stocks').stream())

    print(f"Local Stock Count: {len(local_stocks)}")
    print(f"Remote Stock Count: {len(remote_stocks)}")

    print("\n[EXTRA IN REMOTE]")
    print(remote_stocks - local_stocks)

    print("\n[MISSING IN REMOTE]")
    print(local_stocks - remote_stocks)

if __name__ == "__main__":
    reconcile()
