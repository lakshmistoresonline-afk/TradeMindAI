import asyncio
import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.container import container
from backend.services.research_replay_service import ResearchReplayService

async def main():
    print("=== TRADEMIND AI: V2.2 HISTORICAL REPLAY ===")

    # 1. Verification
    from backend.services.freeze_verification_service import V22FreezeVerificationService
    verify = V22FreezeVerificationService.verify_freeze()
    if verify["status"] != "PASS":
        print(f"CRITICAL: V2.2 Freeze Violation detected. Replay aborted.\n{verify}")
        return

    # 2. Setup Replay Window
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=30)

    print(f"Replay Period: {start_date.date()} to {end_date.date()}")

    # 3. Run Replay
    # Limit to 5 symbols for verification
    original_symbols = container.universe_service.NIFTY_200_CONSTITUENTS
    container.universe_service.NIFTY_200_CONSTITUENTS = original_symbols[:5]
    results = await ResearchReplayService.run_full_replay(start_date, end_date)

    print(f"\nReplay Completed.")
    print(f"Run ID: {results['run_id']}")
    print(f"Symbols Evaluated: {results['total_symbols']}")
    print(f"Signals Generated: {results['signals_generated']}")

    # 4. Save results summary
    import json
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/replay_{results['run_id']}.json", "w") as f:
        json.dump(results, f, default=str, indent=2)

    print(f"Detailed accounting saved to reports/replay_{results['run_id']}.json")

if __name__ == "__main__":
    asyncio.run(main())
