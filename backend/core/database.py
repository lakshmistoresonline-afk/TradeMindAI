import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from backend.core.config import settings
from google.cloud import firestore as google_firestore
from google.oauth2 import service_account

import datetime
from pydantic import BaseModel

# Global client cache
_db_client = None

class PydanticJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)

def get_db():
    global _db_client
    if _db_client is not None:
        return _db_client

    firebase_creds_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if firebase_creds_json:
        try:
            creds_input = firebase_creds_json.strip().strip("'").strip('"')
            creds_dict = None

            # 1. Try Raw JSON
            if creds_input.startswith('{'):
                try:
                    creds_dict = json.loads(creds_input)
                except: pass

            # 2. Try Base64
            if not creds_dict:
                import base64
                import re
                clean_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', creds_input)
                try:
                    if len(clean_b64) % 4 != 0:
                        clean_b64 += '=' * (4 - len(clean_b64) % 4)

                    decoded_bytes = base64.b64decode(clean_b64)
                    decoded = decoded_bytes.decode('utf-8')
                    if decoded.strip().startswith('{'):
                        creds_dict = json.loads(decoded)
                except: pass

            if creds_dict:
                if 'private_key' in creds_dict:
                    pk = creds_dict['private_key']
                    pk = pk.replace('\\\\n', '\n').replace('\\n', '\n').strip()
                    creds_dict['private_key'] = pk

                try:
                    g_creds = service_account.Credentials.from_service_account_info(creds_dict)
                    _db_client = google_firestore.Client(project=creds_dict.get('project_id'), credentials=g_creds)
                    print("[+] Firestore client created.")
                    return _db_client
                except Exception as e:
                    print(f"[!!] Firestore client creation failed: {e}")
        except Exception as e:
            print(f"[!!] Firebase credential parsing failed: {e}")

    # Fallback to local files
    for path in ["service-account.json", "backend/service-account.json"]:
        if os.path.exists(path):
            try:
                _db_client = google_firestore.Client.from_service_account_json(path)
                print(f"[+] Firestore initialized from local file: {path}")
                return _db_client
            except: pass

    print("[!] Firestore initialization skipped.")
    return None

# Lazy Proxy to prevent import-time hangs
class LazyDBClient:
    def __getattr__(self, name):
        client = get_db()
        if client is None:
            raise RuntimeError("Firestore client not initialized.")
        return getattr(client, name)

    def __bool__(self):
        return get_db() is not None

db_client = LazyDBClient()
