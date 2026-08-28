import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate('backend/service-account.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

print("--- Firestore Verification ---")

# Check Summary
summary_ref = db.collection("shadow_summary").document("latest")
summary_doc = summary_ref.get()
if summary_doc.exists:
    summary = summary_doc.to_dict()
    print(f"Summary Found: {json.dumps(summary, indent=2, default=str)}")
else:
    print("Summary latest NOT FOUND")

# Check Active Signals
signals_ref = db.collection("shadow_signals").where("status", "==", "ACTIVE")
docs = signals_ref.stream()
active_signals = []
for doc in docs:
    active_signals.append(doc.to_dict())

print(f"Active Signals Count: {len(active_signals)}")
for s in active_signals:
    print(f" - {s.get('symbol')} ({s.get('timestamp')})")
