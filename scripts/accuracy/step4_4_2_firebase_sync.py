import os
import sys
import json
import pandas as pd
import subprocess
import math
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.cloud import firestore as google_firestore

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

PROJECT_ID = "com-webcraft-trademindai-c8f75"

def get_access_token():
    try:
        token = subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
        return token
    except Exception as e:
        print(f"[!!] Failed to get access token via gcloud: {e}")
        return None

def get_db():
    token = get_access_token()
    if not token:
        return None

    try:
        from google.oauth2 import credentials as oauth2_credentials
        creds = oauth2_credentials.Credentials(token)
        db = google_firestore.Client(project=PROJECT_ID, credentials=creds)
        print(f"[+] Connected to Firestore project: {PROJECT_ID}")
        return db
    except Exception as e:
        print(f"[!!] Firestore client init failed: {e}")
        return None

def sync_data():
    db = get_db()
    if not db:
        print("[!!] Could not connect to Firestore.")
        return

    data_dir = Path("data/results/step4_4_2")

    # 1. Sync Stocks (NIFTY 200)
    print("[*] Syncing Stocks...")
    import sqlite3
    conn = sqlite3.connect('backend/local_operational.db')
    stocks_df = pd.read_sql_query("SELECT * FROM stocks WHERE index_membership = 'NIFTY_200'", conn)
    conn.close()

    batch = db.batch()
    count = 0
    for _, row in stocks_df.iterrows():
        doc_ref = db.collection("stocks").document(row['symbol'])

        m_cap = row['market_cap']
        if pd.isna(m_cap) or m_cap is None: m_cap = 0

        l_price = row['last_price']
        if pd.isna(l_price) or l_price is None: l_price = 0.0

        data = {
            "name": str(row['name']) if not pd.isna(row['name']) else row['symbol'],
            "sector": str(row['sector']) if not pd.isna(row['sector']) else "Unknown",
            "industry": str(row['industry']) if not pd.isna(row['industry']) else "Unknown",
            "last_price": float(l_price),
            "market_cap": int(m_cap),
            "is_fno": bool(row['is_fno']),
            "index_membership": str(row['index_membership']),
            "updated_at": google_firestore.SERVER_TIMESTAMP
        }
        batch.set(doc_ref, data, merge=True)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f"[+] Synced {count} stocks.")

    # 2. Sync Portfolio Equity
    print("[*] Syncing Portfolio Equity...")
    equity_path = data_dir / "wf_portfolio_equity.csv"
    if equity_path.exists():
        e_df = pd.read_csv(equity_path)
        batch = db.batch()
        count = 0
        for _, row in e_df.iterrows():
            date_str = str(row['date']).split(' ')[0]
            doc_ref = db.collection("portfolio_equity").document(date_str)

            try:
                dt_str = str(row['date']).replace('Z', '').replace(' ', 'T')
                if 'T' not in dt_str: dt_str += 'T00:00:00'
                dt = datetime.fromisoformat(dt_str)
            except Exception as e:
                dt = datetime.utcnow()

            data = {
                "date": dt,
                "equity": float(row['equity']),
                "cash": float(row['cash']),
                "open_positions": int(row['pos_count']),
                "updated_at": google_firestore.SERVER_TIMESTAMP
            }
            batch.set(doc_ref, data, merge=True)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"[+] Synced {count} equity records.")

    # 3. Sync Performance Summary
    print("[*] Syncing Performance Summary...")
    trades_path = data_dir / "wf_portfolio_trades.csv"
    if equity_path.exists() and trades_path.exists():
        t_df = pd.read_csv(trades_path)
        e_df = pd.read_csv(equity_path)
        final_eq = e_df['equity'].iloc[-1]
        summary_data = {
            "total_net_pnl": float(final_eq - 1000000),
            "total_return_pct": float((final_eq / 1000000 - 1) * 100),
            "trade_count": len(t_df),
            "win_rate": float((len(t_df[t_df['pnl'] > 0]) / len(t_df)) * 100),
            "last_updated": google_firestore.SERVER_TIMESTAMP,
            "validation_status": "STEP4.4.2_VALIDATION_COMPLETE",
            "strategy_version": "v2.2"
        }
        db.collection("performance_summary").document("latest").set(summary_data)
        print("[+] Synced performance summary.")

    print("[SUCCESS] Firebase synchronization complete.")

if __name__ == "__main__":
    sync_data()
