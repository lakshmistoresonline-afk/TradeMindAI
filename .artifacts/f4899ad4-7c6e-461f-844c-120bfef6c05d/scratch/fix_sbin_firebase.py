
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
import subprocess

def get_access_token():
    try:
        return subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
    except: return None

def main():
    token = get_access_token()
    if not token:
        print("Could not get token.")
        return

    from google.oauth2 import credentials as oauth2_credentials
    from google.cloud import firestore as google_firestore
    creds = oauth2_credentials.Credentials(token)
    db = google_firestore.Client(project="com-webcraft-trademindai-c8f75", credentials=creds)

    doc_ref = db.collection("shadow_signals").document("sig_SBIN_202608180715")
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        print(f"Current SBIN Status: {data.get('status')}")
        if data.get('status') == 'ACTIVE':
            print("Updating SBIN to TARGET_HIT...")
            doc_ref.update({
                "status": "TARGET_HIT",
                "net_return": 2.80,
                "updated_at": google_firestore.SERVER_TIMESTAMP
            })
            print("Update complete.")
        else:
            print("SBIN is not ACTIVE in Firebase. No update needed.")
    else:
        print("SBIN signal not found in Firebase.")

if __name__ == "__main__":
    main()
