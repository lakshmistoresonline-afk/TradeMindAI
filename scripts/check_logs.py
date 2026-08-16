import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def check_logs():
    db_path = 'backend/service-account.json'
    if not os.path.exists(db_path):
         db_path = 'service-account.json'

    cred = credentials.Certificate(db_path)
    try:
        app = firebase_admin.initialize_app(cred)
    except:
        app = firebase_admin.get_app()

    db = firestore.client()

    print("\n--- TRADE MIND AI: RECENT SYSTEM LOGS ---\n")
    logs = db.collection("system_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(30).stream()

    for log in logs:
        data = log.to_dict()
        print(f"[{data.get('timestamp')}] {data.get('type')} | Symbol: {data.get('symbol')} | Step: {data.get('step')} | Error: {str(data.get('error'))[:150]}")

if __name__ == "__main__":
    check_logs()
