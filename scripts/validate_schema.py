import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import ValidationError
import sys

# Add backend to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.domain.models.stock import Stock

def validate():
    firebase_creds_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not firebase_creds_json:
        print("SKIP: No Firebase credentials for automated gate.")
        return

    cred = credentials.Certificate(json.loads(firebase_creds_json))
    try:
        app = firebase_admin.initialize_app(cred)
    except:
        app = firebase_admin.get_app()

    db = firestore.client()

    print("--- QUALITY GATE: FIRESTORE SCHEMA VALIDATION ---")

    # 1. Validate Stocks
    stocks = db.collection("stocks").limit(10).stream()
    for doc in stocks:
        data = doc.to_dict()
        try:
            Stock(**data)
            print(f"✅ {data['symbol']}: Schema Valid")
        except ValidationError as e:
            print(f"❌ {data.get('symbol', 'Unknown')}: Schema Error - {e}")

    print("--- VALIDATION COMPLETE ---")

if __name__ == "__main__":
    validate()
