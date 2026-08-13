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
        # Vision 2.2: Ultra-resilient Base64 & Minified JSON Parser
        creds_dict = None
        print(f"[*] Raw Credential Length: {len(firebase_creds_json)}")

        try:
            import base64
            import re
            # Strip anything that isn't a Base64 character to avoid truncation artifacts
            clean_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', firebase_creds_json)
            print(f"[*] Cleaned Base64 Length: {len(clean_b64)}")

            decoded = base64.b64decode(clean_b64).decode('utf-8')
            creds_dict = json.loads(decoded)
            print("[+] Firebase Credentials decoded from Base64")
        except Exception as e:
            print(f"[*] Base64 decode failed, trying raw minified JSON: {e}")
            try:
                # Handle minified JSON with escaped newlines
                clean_json = firebase_creds_json.replace("\\n", "\n")
                creds_dict = json.loads(clean_json)
                print("[+] Firebase Credentials loaded from Raw JSON")
            except:
                print("[!] All Firebase credential parsing failed.")

        if creds_dict:
            try:
                cred = credentials.Certificate(creds_dict)
                app = firebase_admin.initialize_app(cred)
                print("[+] Firebase Admin initialized successfully.")
            except Exception as e:
                print(f"[!] Firebase App Initialization Failed: {e}")
                # Last stand fallback: Default credentials
                try:
                    app = firebase_admin.initialize_app(options={'projectId': settings.FIREBASE_PROJECT_ID})
                    print("[+] Firebase Fallback initialized.")
                except: pass
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

db_client = None

try:
    db_client = firestore.client()
except Exception as e:
    print(f"[!] Firestore Client Initialization Failed: {e}")

def get_db():
    """
    Dependency to get Firestore client.
    """
    if db_client is None:
        print("[!] Warning: get_db called but db_client is None")
    return db_client
