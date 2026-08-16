import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from backend.core.config import settings

# Initialize Firebase Admin SDK
app = None
db_client = None

firebase_creds_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if firebase_creds_json:
    print(f"[*] Raw Credential Length: {len(firebase_creds_json)}")
    try:
        import base64
        import re
        # Resilient Base64 Cleanup
        clean_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', firebase_creds_json)
        decoded = base64.b64decode(clean_b64).decode('utf-8')
        creds_dict = json.loads(decoded)
        cred = credentials.Certificate(creds_dict)
        app = firebase_admin.initialize_app(cred)
        db_client = firestore.client()
        print("[+] Firebase initialized from Base64")
    except Exception as b64_err:
        print(f"[*] Base64 init failed ({b64_err}), trying Raw JSON...")
        try:
            # Try raw JSON with repair
            clean_json = firebase_creds_json.strip().strip("'").strip('"').replace("\\n", "\n")
            creds_dict = json.loads(clean_json)
            cred = credentials.Certificate(creds_dict)
            app = firebase_admin.initialize_app(cred)
            db_client = firestore.client()
            print("[+] Firebase initialized from Raw JSON")
        except Exception as json_err:
            print(f"[!] Firebase Init Failed completely: {json_err}")
            # Final fallback: initialize with just project ID
            try:
                app = firebase_admin.initialize_app(options={'projectId': settings.FIREBASE_PROJECT_ID})
                db_client = firestore.client()
                print("[+] Firebase Fallback initialized (Read-Only/Limited)")
            except Exception as final_err:
                print(f"[!!] Total Firebase Failure: {final_err}")

# Local file fallbacks if no environment variable or if it failed
if db_client is None:
    for path in ["service-account.json", "backend/service-account.json"]:
        if os.path.exists(path):
            try:
                cred = credentials.Certificate(path)
                app = firebase_admin.initialize_app(cred)
                db_client = firestore.client()
                print(f"[+] Firebase initialized from local file: {path}")
                break
            except: pass

def get_db():
    return db_client
