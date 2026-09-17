import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import asyncio
import sys
import datetime

sys.path.append(os.getcwd())
from backend.core.container import container
from backend.services.signal_auditor import SignalAuditor

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

async def sync():
    print("=== TRADEMIND AI: MASTER LIFECYCLE SYNC ===")

    auditor = SignalAuditor(container.ios_repo)

    # We want to re-run the audit logic for all current unclosed signals
    print("[*] Fetching non-terminal signals...")
    all_signals = await container.ios_repo.get_all_live_signals()
    non_terminal = [s for s in all_signals if s.status in ["WAITING_FOR_ENTRY", "ENTRY_TRIGGERED", "ACTIVE"]]

    print(f"[*] Found {len(non_terminal)} signals to re-evaluate.")

    for signal in non_terminal:
        print(f"   Re-evaluating {signal.symbol} ({signal.id}). Current Status: {signal.status}")
        # Note: SignalAuditor uses yfinance internally which is fine for a one-time script
        await auditor._audit_single_signal(signal)

    print("\n[+] Lifecycle Sync Complete.")

if __name__ == "__main__":
    asyncio.run(sync())
