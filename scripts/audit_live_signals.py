import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container
from backend.services.signal_auditor import SignalAuditor

async def main():
    print("--- TRADEMIND AI: SIGNAL OUTCOME AUDITOR ---")

    # Vision 2.2: Register PG JSON adapters to prevent OID 114 errors
    try:
        import psycopg2
        from psycopg2.extras import register_default_jsonb
        # Get raw connection to register
        from backend.core.postgres import engine
        raw_conn = engine.raw_connection()
        register_default_jsonb(conn_or_curs=raw_conn)
        print("[+] Postgres JSON adapters registered.")
    except Exception as e:
        print(f"[*] Adapter registration skipped: {e}")

    print("[*] Initiating Forensic Audit of Live & Historical Signals...")

    # Use the hybrid repository
    repo = container.ios_repo
    auditor = SignalAuditor(repo)

    # Resolve all non-terminal signals
    # Our Auditor is now enhanced to handle WAITING_FOR_ENTRY and ACTIVE
    await auditor.audit_active_signals()

    print("\n--- AUDIT COMPLETE: ALL SIGNAL OUTCOMES SYNCHRONIZED ---")

if __name__ == "__main__":
    asyncio.run(main())
