import os
import sys
import argparse
import asyncio
import json
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.ingestion_service import IngestionService
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

CHECKPOINT_FILE = "backend/data/sync_checkpoint.json"

class SyncManager:
    def __init__(self, args):
        self.args = args
        self.ingestion_service = IngestionService(container.repository, container.provider)
        self.checkpoint = self._load_checkpoint()

    def _load_checkpoint(self) -> Dict[str, Any]:
        if self.args.resume and os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, 'r') as f:
                    data = f.read()
                    if not data: return {}
                    return json.loads(data)
            except Exception as e:
                print(f"[!] Warning: Could not load checkpoint: {e}")
        return {}

    def _save_checkpoint(self):
        try:
            os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(self.checkpoint, f, indent=4, default=str)
        except Exception as e:
            print(f"[!] Warning: Could not save checkpoint: {e}")

    async def run(self):
        print(f"============================================================")
        print(f" TRADEMIND AI - HISTORICAL DATA SYNCHRONIZATION")
        print(f"============================================================")

        universe = []
        if self.args.universe == "NIFTY_200":
            universe = NIFTY_200_CONSTITUENTS
        elif self.args.symbols:
            universe = self.args.symbols.split(",")

        if not universe:
            print("[!] ERROR: No symbols identified for synchronization.")
            sys.exit(1)

        print(f"[*] Universe: {self.args.universe}")
        print(f"[*] Total symbols: {len(universe)}")
        print(f"[*] Timeframe: {self.args.timeframe}")
        print(f"[*] Start Date: {self.args.start_date}")
        print(f"[*] Resume Mode: {self.args.resume}")

        start_dt = datetime.datetime.fromisoformat(self.args.start_date)
        end_dt = datetime.datetime.fromisoformat(self.args.end_date) if self.args.end_date else datetime.datetime.utcnow()

        # Ensure timezone awareness if required by provider (handled in ingestion service)

        successful = 0
        failed = 0
        skipped = 0

        for symbol in universe:
            # Check Resume
            if self.args.resume and symbol in self.checkpoint:
                if self.checkpoint[symbol].get("status") == "SUCCESS":
                    # For incremental, we might want to check last date, but for P0 gate, we skip if marked success
                    print(f"   [SKIP] {symbol} already synchronized successfully.")
                    skipped += 1
                    continue

            print(f"[*] Syncing {symbol} ({successful + failed + skipped + 1}/{len(universe)})...")

            if self.args.dry_run:
                print(f"   [DRY-RUN] Would sync {symbol} from {start_dt.date()} to {end_dt.date()}")
                successful += 1
                continue

            try:
                # Use IngestionService for robust sync
                result = await self.ingestion_service.ingest_historical_data(
                    symbol=symbol,
                    start_date=start_dt,
                    end_date=end_dt,
                    interval=self.args.timeframe
                )

                if result["status"] == "SUCCESS":
                    print(f"   [SUCCESS] {symbol}: {result['count']} candles ingested.")
                    self.checkpoint[symbol] = {
                        "status": "SUCCESS",
                        "count": result["count"],
                        "last_date": result["end"],
                        "updated_at": datetime.datetime.utcnow()
                    }
                    successful += 1
                else:
                    print(f"   [FAILED] {symbol}: {result.get('reason', 'Unknown error')}")
                    self.checkpoint[symbol] = {
                        "status": "FAILED",
                        "error": result.get("reason"),
                        "updated_at": datetime.datetime.utcnow()
                    }
                    failed += 1

            except Exception as e:
                print(f"   [ERROR] {symbol}: {str(e)}")
                self.checkpoint[symbol] = {
                    "status": "ERROR",
                    "error": str(e),
                    "updated_at": datetime.datetime.utcnow()
                }
                failed += 1

            # Save checkpoint after each symbol for safety
            self._save_checkpoint()

            # Rate limiting / Courtesy delay
            await asyncio.sleep(0.2)

        print(f"\n============================================================")
        print(f" SYNC SUMMARY")
        print(f"============================================================")
        print(f"Attempted: {len(universe)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        print(f"============================================================")

        if failed > 0:
            print(f"[!] Warning: {failed} symbols failed to sync.")
            # sys.exit(1) # We might not want to hard fail the whole stage if most succeeded, but for P0 gate, we should be strict.
            # Decision: Return non-zero if successful < expected

        if successful + skipped < len(universe):
             sys.exit(1)
        else:
             sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TradeMind AI - Historical Market Data Sync")
    parser.add_argument("--universe", choices=["NIFTY_200", "CUSTOM"], default="NIFTY_200")
    parser.add_argument("--symbols", type=str, help="Comma separated list for CUSTOM universe")
    parser.add_argument("--start-date", default="2020-01-01", help="YYYY-MM-DD")
    parser.add_argument("--end-date", help="YYYY-MM-DD (defaults to now)")
    parser.add_argument("--timeframe", default="1D", help="1D, 1h, 15m etc")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", action="store_false", dest="resume")
    parser.add_argument("--retry", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    manager = SyncManager(args)
    asyncio.run(manager.run())
