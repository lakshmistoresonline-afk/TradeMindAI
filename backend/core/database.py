import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from backend.core.config import settings

# Initialize Firebase Admin SDK
try:
    app = firebase_admin.get_app()
except ValueError:
    # 1. Try to load from Environment Variable (Best for Production/Render)
    firebase_creds_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if firebase_creds_json:
        # Vision 2.2: Ultra-resilient parsing (Minified JSON or Base64)
        try:
            # 1. Try raw JSON parse
            creds_dict = json.loads(firebase_creds_json)
            print("[+] Firebase Credentials loaded from Raw JSON")
        except:
            try:
                # 2. Try Base64 decode
                import base64
                clean_b64 = firebase_creds_json.strip("'").strip('"')
                decoded = base64.b64decode(clean_b64).decode('utf-8')
                creds_dict = json.loads(decoded)
                print("[+] Firebase Credentials decoded from Base64")
            except Exception as e:
                print(f"[!] Critical: Firebase Credential Parsing Failed: {e}")
                creds_dict = {}

        if creds_dict:
            cred = credentials.Certificate(creds_dict)
            app = firebase_admin.initialize_app(cred)
    # 2. Try to load from local file (Best for Development)
    elif os.path.exists("service-account.json"):
        cred = credentials.Certificate("service-account.json")
        app = firebase_admin.initialize_app(cred)
    elif os.path.exists("backend/service-account.json"):
        cred = credentials.Certificate("backend/service-account.json")
        app = firebase_admin.initialize_app(cred)
    else:
        # 3. Fallback to default
        app = firebase_admin.initialize_app(options={
            'projectId': settings.FIREBASE_PROJECT_ID,
        })

db_client = firestore.client()

def get_db():
    """
    Dependency to get Firestore client.
    """
    return db_client
