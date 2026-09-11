import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.container import container
from backend.services.equity_signal_generation_service import EquitySignalGenerationService

async def main():
    print("=== [EQUITY] Full Universe Production Scan ===")

    # Ensure environment is set to shadow or production for LIVE_SHADOW mode
    os.environ["ENVIRONMENT"] = "shadow"

    report = await EquitySignalGenerationService.run_production_scan()

    print("\n--- SCAN REPORT ---")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Universe: {report['universe_count']}")
    print(f"Signals Generated: {report['signals_generated']}")
    print(f"Errors: {len(report['errors'])}")
    print(f"Duration: {report['duration_seconds']:.2f}s")

    if report['errors']:
        print("\nTop Errors:")
        for e in report['errors'][:10]:
            print(f"  {e['symbol']}: {e['error']}")

if __name__ == "__main__":
    asyncio.run(main())
