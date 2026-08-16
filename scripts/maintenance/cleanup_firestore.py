import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.database import db_client

def cleanup_backtests():
    if db_client is None:
        print("[!] Firestore not initialized.")
        return

    print("[*] Auditing Firestore Backtest signals...")

    backtests = db_client.collection("backtests").stream()
    total_deleted = 0

    for bt in backtests:
        symbol = bt.id
        signals_ref = db_client.collection("backtests").document(symbol).collection("signals")
        signals = signals_ref.stream()

        for s in signals:
            data = s.to_dict()
            asset = data.get("asset_class")

            is_corrupt = False
            if asset == "OPTIONS":
                if data.get("strike") is None or data.get("option_type") is None:
                    is_corrupt = True

            if is_corrupt:
                print(f"   [PURGE] Deleting corrupt signal {s.id} for {symbol}")
                signals_ref.document(s.id).delete()
                total_deleted += 1

    print(f"\n[SUCCESS] Purged {total_deleted} corrupt signals from Firestore.")

if __name__ == "__main__":
    cleanup_backtests()
