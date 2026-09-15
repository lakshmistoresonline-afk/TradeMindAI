import asyncio
import datetime
import sys
import os
import sqlalchemy
from dotenv import load_dotenv

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

# Force production environment
os.environ["ENVIRONMENT"] = "production"

from backend.core.container import container
from sqlalchemy import text

async def run_scan():
    print("=== Starting NEON Multi-Horizon Signal Scan ===")

    # 1. Clear old signals from Neon
    db_url = os.getenv("POSTGRES_URL")
    engine = sqlalchemy.create_engine(db_url)
    with engine.connect() as conn:
        print("[*] Clearing live_signals table in Neon...")
        conn.execute(text("DELETE FROM live_signals"))
        conn.commit()

    # 2. Run scan
    service = container.equity_signal_generation_service
    report = await service.run_production_scan()

    print(f"Scan Completed. Signals Generated: {report['signals_generated']}")
    if report['errors']:
        print(f"Errors encountered: {len(report['errors'])}")

if __name__ == "__main__":
    asyncio.run(run_scan())
