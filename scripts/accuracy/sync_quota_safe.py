import os
import sys
import json
import pandas as pd
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"
load_dotenv('backend/.env')

from google.cloud import firestore as google_firestore
from google.api_core import exceptions

PROJECT_ID = "com-webcraft-trademindai-c8f75"
QUEUE_FILE = Path("data/firebase/firebase_sync_queue.json")

class QuotaSafeSyncEngine:
    def __init__(self):
        self.db = self._get_db()
        self.queue = self._load_queue()
        self.batch_size = 20
        self.max_writes = 50
        self.writes_performed = 0

    def _get_access_token(self):
        try:
            token = subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
            return token
        except:
            return None

    def _get_db(self):
        token = self._get_access_token()
        if not token: return None
        try:
            from google.oauth2 import credentials as oauth2_credentials
            creds = oauth2_credentials.Credentials(token)
            return google_firestore.Client(project=PROJECT_ID, credentials=creds)
        except:
            return None

    def _load_queue(self):
        if QUEUE_FILE.exists():
            try:
                with open(QUEUE_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        return {"pending": [], "completed": [], "failed": []}

    def _save_queue(self):
        with open(QUEUE_FILE, 'w') as f:
            json.dump(self.queue, f, indent=4)

    def add_to_queue(self, collection_path, doc_id, data, priority=10):
        item_key = f"{collection_path}/{doc_id}"
        if any(i['id'] == item_key for i in self.queue['pending']):
            return

        serializable_data = {}
        for k, v in data.items():
            if isinstance(v, datetime):
                serializable_data[k] = {"__type__": "datetime", "value": v.isoformat()}
            elif isinstance(v, pd.Timestamp):
                serializable_data[k] = {"__type__": "datetime", "value": v.to_pydatetime().isoformat()}
            else:
                serializable_data[k] = v

        self.queue['pending'].append({
            "id": item_key, "collection_path": collection_path, "doc_id": doc_id,
            "data": serializable_data, "priority": priority, "added_at": datetime.utcnow().isoformat()
        })

    async def run_sync(self):
        if not self.db:
            print("[FAIL] Firestore connection failed.")
            return

        print(f"[*] Starting Quota-Safe Sync. Pending items: {len(self.queue['pending'])}")
        self.queue['pending'].sort(key=lambda x: x['priority'])

        while self.queue['pending'] and self.writes_performed < self.max_writes:
            item = self.queue['pending'][0]

            doc_data = {}
            for k, v in item['data'].items():
                if isinstance(v, dict) and v.get("__type__") == "datetime":
                    doc_data[k] = datetime.fromisoformat(v['value'])
                else:
                    doc_data[k] = v

            parts = item['collection_path'].split('/')
            ref = self.db
            for part in parts:
                if ref is self.db: ref = ref.collection(part)
                elif isinstance(ref, google_firestore.CollectionReference): ref = ref.document(part)
                else: ref = ref.collection(part)

            doc_ref = ref.document(item['doc_id'])

            try:
                snapshot = doc_ref.get()
                if snapshot.exists:
                    if self._data_matches(snapshot.to_dict(), doc_data):
                        self.queue['completed'].append(self.queue['pending'].pop(0))
                        continue
            except exceptions.ResourceExhausted:
                print("[!!] QUOTA EXCEEDED (Read). Stopping.")
                break
            except Exception as e:
                print(f"   [!] Error checking {item['id']}: {e}")

            try:
                doc_ref.set(doc_data, merge=True)
                self.writes_performed += 1
                self.queue['completed'].append(self.queue['pending'].pop(0))
                print(f"   [+] Synced {item['id']} ({self.writes_performed}/{self.max_writes})")
            except exceptions.ResourceExhausted:
                print("[!!] QUOTA EXCEEDED (Write). Stopping.")
                break
            except Exception as e:
                print(f"   [!] Error writing {item['id']}: {e}")
                it = self.queue['pending'].pop(0)
                it['error'] = str(e)
                self.queue['failed'].append(it)

        self._save_queue()
        print(f"[FINISH] Session complete. Performed {self.writes_performed} writes.")

    def _data_matches(self, existing, new_data):
        for k, v in new_data.items():
            if k in ['updated_at', 'synced_at', 'last_sync']: continue
            if k not in existing: return False
            if isinstance(v, datetime):
                if str(existing[k])[:19] != v.isoformat()[:19]: return False
            elif existing[k] != v: return False
        return True

    def build_minimal_queue(self):
        print("[*] Building Minimal Sync Queue (SQLite)...")
        self.queue['pending'] = []
        conn = sqlite3.connect("backend/local_operational.db")

        # 1. System Status
        self.add_to_queue("system_status", "latest", {"status": "OPERATIONAL_SAFE", "version": "v2.2"}, priority=1)

        # 2. Performance
        summaries = {
            "backtest": {"total_return": 1747.16, "win_rate": 49.77, "trades": 6882, "status": "VERIFIED"},
            "walk_forward": {"total_return": 2757.34, "win_rate": 52.57, "trades": 4489, "status": "VALIDATED"}
        }
        for k, v in summaries.items():
            self.add_to_queue("performance_summary", k, v, priority=2)

        # 3. Stocks (Sample 20 for test)
        stocks = pd.read_sql_query("SELECT symbol, name, sector FROM stocks LIMIT 20", conn)
        for _, row in stocks.iterrows():
            self.add_to_queue("stocks", row['symbol'], {
                "name": str(row['name']), "sector": str(row['sector']), "status": "OPERATIONAL"
            }, priority=3)

        conn.close()
        self._save_queue()
        print(f"[SUCCESS] Minimal Queue built. Total pending: {len(self.queue['pending'])}")

if __name__ == "__main__":
    engine = QuotaSafeSyncEngine()
    if "--build" in sys.argv:
        engine.build_minimal_queue()
    import asyncio
    asyncio.run(engine.run_sync())
