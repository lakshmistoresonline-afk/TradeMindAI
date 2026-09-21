import asyncio
import datetime
import time
import os
import sys
import uuid
from datetime import timezone

# Add project root to path
sys.path.append(os.getcwd())

# Ensure environment is set for local execution
os.environ["ENVIRONMENT"] = "development"

from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.services.market_data_service import MarketDataService
from backend.scripts.mirror_local_to_firestore import mirror
from backend.services.market_calendar import MarketCalendar

async def run_price_update_cycle():
    """
    High-Frequency Task: Every 5 Minutes
    Updates prices for active trades and checks for Target/Stop hits.
    """
    print(f"\n--- [PRICE UPDATE] {datetime.datetime.now().strftime('%H:%M:%S')} ---")
    try:
        if MarketCalendar.is_market_open():
            execution_id = str(uuid.uuid4())
            await MarketDataService.sync_active_signal_prices(execution_id=execution_id)
        else:
            print("[*] Market Closed. Skipping price refresh.")
    except Exception as e:
        print(f"[!] Price Update Error: {e}")

async def run_generation_cycle():
    """
    Medium-Frequency Task: Every 15 Minutes
    Scans universe for new signals and mirrors all data to cloud.
    """
    print(f"\n{'='*60}")
    print(f"[*] MASTER GENERATION CYCLE: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    try:
        # 1. Generate New Signals
        report = await EquitySignalGenerationService.run_production_scan()
        print(f"      [+] Signals Generated: {report.get('signals_generated', 0)}")

        # 2. Mirror to Cloud (Firebase)
        print("[*] Syncing to TradeMind Web App...")
        await mirror()

        # 3. Emit Heartbeat & Market Context
        from backend.core.database import db_client
        if db_client:
            # Fetch latest market state for cloud visibility
            market_state = await MarketDataService.get_market_state()

            db_client.collection("system_metrics").document("local_master").set({
                "last_run": datetime.datetime.now(timezone.utc),
                "status": "HEALTHY",
                "mode": "V2.3_SHADOW_MASTER",
                "pc": os.getenv("COMPUTERNAME", "Local_Workstation"),
                "market_context": market_state
            })

    except Exception as e:
        print(f"[!] Generation Cycle Error: {e}")

async def main():
    print("=== [TradeMind AI] Local Master Update Engine ===")
    print("Authority: V2.3 Shadow Mode")
    print("Timers: 5m (Price/Risk) | 15m (Scan/Sync)")
    print("Press CTRL+C to stop.")

    # Initialize counters
    cycle_count = 0

    while True:
        # 1. Every loop (Every 5 mins) -> Run Price Update
        await run_price_update_cycle()

        # 2. Every 3rd loop (Every 15 mins) -> Run Signal Generation
        if cycle_count % 3 == 0:
            await run_generation_cycle()

        cycle_count += 1

        print(f"\n[*] All tasks complete. Resting for 5 minutes...")
        await asyncio.sleep(300) # 5 Minute Sleep

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Master Engine stopped by user.")
