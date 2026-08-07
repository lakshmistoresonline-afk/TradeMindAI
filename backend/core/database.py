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
        creds_dict = json.loads(firebase_creds_json)
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
