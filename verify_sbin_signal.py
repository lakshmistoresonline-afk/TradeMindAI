import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('backend/service-account.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

doc_id = "sig_SBIN_202608181011"
doc = db.collection("shadow_signals").document(doc_id).get()

if doc.exists:
    print(f"Signal {doc_id} found in Firestore:")
    print(doc.to_dict())
else:
    # Try searching by symbol if ID is different
    print(f"Signal {doc_id} NOT found in Firestore. Searching by symbol SBIN...")
    docs = db.collection("shadow_signals").where("symbol", "==", "SBIN").stream()
    for d in docs:
        print(f"Found signal {d.id}: {d.to_dict().get('status')}")
