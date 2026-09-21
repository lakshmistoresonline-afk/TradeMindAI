import asyncio
import datetime
import time
import os
import sys
from datetime import timezone

# Add project root to path
sys.path.append(os.getcwd())

# Ensure environment is set for local execution
os.environ["ENVIRONMENT"] = "development"

from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.scripts.mirror_local_to_firestore import mirror

async def pulse_cycle():
    print(f"\n{'='*60}")
    print(f"[*] Starting Local Pulse Cycle: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    try:
        # 1. Run Production Scan (Generates Active Signals)
        # This ingests latest data and runs V2.2 logic with V2.3 Shadowing
        print("[1/3] Running Signal Scan (Top 50 NIFTY 200)...")
        report = await EquitySignalGenerationService.run_production_scan()
        print(f"      [+] Scan Complete. Signals: {report.get('signals_generated', 0)}, Errors: {len(report.get('errors', []))}")

        # 2. Sync to Global Web App
        print("[2/3] Mirroring Local State to Firebase Firestore...")
        await mirror()
        print("      [+] Mirroring Successful.")

        # 3. Heartbeat Update
        print("[3/3] Emitting System Heartbeat...")
        from backend.core.database import db_client
        if db_client:
            db_client.collection("system_metrics").document("local_pulse").set({
                "last_run": datetime.datetime.now(timezone.utc),
                "status": "HEALTHY",
                "signals_last_cycle": report.get('signals_generated', 0),
                "pc_identity": os.getenv("COMPUTERNAME", "Local_Workstation")
            })

    except Exception as e:
        print(f"[!] CRITICAL ERROR in Pulse Cycle: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("=== [TradeMind AI] Local Operational Pulse Worker ===")
    print("Enforcing 15-minute update interval (V2.3 Shadow Mode).")
    print("Press CTRL+C to stop.")

    interval_seconds = 15 * 60 # 15 Minutes

    while True:
        start_time = time.time()

        await pulse_cycle()

        elapsed = time.time() - start_time
        sleep_time = max(0, interval_seconds - elapsed)

        next_run = datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)
        print(f"\n[*] Cycle complete. Next run at: {next_run.strftime('%H:%M:%S')}")
        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Local Pulse Worker stopped by user.")
