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
        creds_dict = None

        # 1. Clean the input (Remove potential surrounding quotes, whitespace and newlines)
        clean_input = firebase_creds_json.strip().strip("'").strip('"').replace("\\n", "\n")

        try:
            # A. Try raw JSON parse first
            creds_dict = json.loads(clean_input)
            print("[+] Firebase Credentials loaded from Raw JSON")
        except:
            try:
                # B. Try Base64 decode (Remove ALL internal whitespace/newlines first)
                import base64
                import re
                # Base64 should not contain whitespace. Strip everything except valid B64 chars.
                pure_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', clean_input)
                decoded = base64.b64decode(pure_b64).decode('utf-8')
                creds_dict = json.loads(decoded)
                print("[+] Firebase Credentials decoded from Base64")
            except Exception as e:
                print(f"[!] Critical: Firebase Credential Parsing Failed: {e}")
                # Fallback: Attempt to fix common JSON escaping in the private key string directly
                try:
                    if '"private_key":' in clean_input:
                        # Attempt a "lazy" fix for common shell escaping issues
                        fixed_json = clean_input.replace("\n", "\\n").replace("\r", "")
                        creds_dict = json.loads(fixed_json)
                        print("[+] Firebase Credentials loaded via Escaping Repair")
                except:
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
