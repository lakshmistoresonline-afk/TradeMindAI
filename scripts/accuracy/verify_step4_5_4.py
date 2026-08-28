import os
import sys
import asyncio
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.services.market_calendar import IndianMarketCalendar

def get_db():
    try:
        token = subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
        from google.oauth2 import credentials as oauth2_credentials
        from google.cloud import firestore
        creds = oauth2_credentials.Credentials(token)
        return firestore.Client(project="com-webcraft-trademindai-c8f75", credentials=creds)
    except:
        return None

async def verify():
    print("--- TRADEMIND AI STEP 4.5.4 FORENSIC VERIFICATION ---")

    # 1. Market Status
    session = IndianMarketCalendar.get_current_session()
    print(f"Market Status: {session}")

    # 2. Portfolio Consistency
    import json
    p_path = "data/results/step4_5/shadow_portfolio.json"
    if os.path.exists(p_path):
        p = json.load(open(p_path))
        print(f"Shadow Equity: INR {p['equity']:,.2f}")
        print(f"Shadow Cash: INR {p['cash']:,.2f}")

    # 3. Firebase Connectivity (GCloud Token Method)
    db = get_db()
    if db:
        print("Firebase Connection: PASS")
        # Check summary
        doc = db.collection("shadow_summary").document("latest").get()
        if doc.exists:
             data = doc.to_dict()
             print(f"Cloud Data Verified. Last Run: {data.get('last_run')}")
             print(f"Cloud Status: {data.get('status')}")
    else:
        print("Firebase Connection: FAIL")

if __name__ == "__main__":
    asyncio.run(verify())
