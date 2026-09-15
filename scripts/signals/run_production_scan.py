import asyncio
import datetime
import sys
import os

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

from backend.core.container import container

async def run_scan():
    print("=== Starting Multi-Horizon Signal Scan (PRODUCTION) ===")
    service = container.equity_signal_generation_service
    report = await service.run_production_scan()
    print(f"Scan Completed. Signals Generated: {report['signals_generated']}")
    if report['errors']:
        print(f"Errors encountered: {len(report['errors'])}")

if __name__ == "__main__":
    asyncio.run(run_scan())
