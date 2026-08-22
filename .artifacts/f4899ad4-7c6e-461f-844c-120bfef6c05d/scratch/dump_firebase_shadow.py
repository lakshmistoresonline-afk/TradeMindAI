
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    # Use the same logic as backend/core/database.py if possible, or just look for service-account.json
    cred_path = "backend/service-account.json"
    if not os.path.exists(cred_path):
        cred_path = "service-account.json"

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback to default project id if no creds (might not work without auth)
        firebase_admin.initialize_app(options={'projectId': 'com-webcraft-trademindai-c8f75'})

    db = firestore.client()

    # 1. Shadow Monitor State
    state_ref = db.collection("shadow_monitor").document("state")
    state = state_ref.get().to_dict()
    print("--- SHADOW MONITOR STATE ---")
    print(json.dumps(state, indent=2, default=str))

    # 2. Check for universe data or signals
    print("\n--- SHADOW MONITOR COLLECTIONS ---")
    collections = db.collection("shadow_monitor").list_documents()
    for doc in collections:
        print(f"Document: {doc.id}")

    # 3. Check live_signals
    print("\n--- LIVE SIGNALS (LATEST 5) ---")
    live_signals = db.collection("live_signals").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).stream()
    for s in live_signals:
        print(f"{s.id}: {s.to_dict().get('symbol')} {s.to_dict().get('timestamp')}")

if __name__ == "__main__":
    main()
