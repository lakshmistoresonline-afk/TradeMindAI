import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.database import get_db

def test_conn():
    print("[*] Testing Firebase connection...")
    db = get_db()
    if db is None:
        print("[!!] Firebase DB client is None.")
        return

    try:
        # Try to list collections
        collections = db.collections()
        print("[+] Successfully connected to Firebase.")
        print("[+] Available collections:")
        for coll in collections:
            print(f"   - {coll.id}")
    except Exception as e:
        print(f"[!!] Connection failed: {e}")

if __name__ == "__main__":
    test_conn()
