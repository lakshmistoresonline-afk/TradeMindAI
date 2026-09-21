import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import db_client

async def test_write():
    print("Testing Firestore Write...")
    try:
        if not db_client:
            print("Firestore client not initialized.")
            return

        doc_ref = db_client.collection("system_test").document("local_sync_check")
        doc_ref.set({
            "message": "Local backend sync test",
            "timestamp": asyncio.get_event_loop().time()
        })
        print("Successfully wrote to Firestore!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_write())
