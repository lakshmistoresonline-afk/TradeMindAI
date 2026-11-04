"""
================================================================================
TradeMindAI: Local Operational 5-Minute Pulse Worker (v3.1)
================================================================================
1. Enforces mandatory Redis distributed lock `lock:pulse` with a 300s lease,
   unique ownership token, background lease renewal task, and compare-and-delete Lua release script.
2. Fails closed with RuntimeError if Redis connectivity is unavailable or if lock ownership is lost.
3. Checks lock ownership before AND after every symbol 5m intraday sync.
4. Synchronizes the full canonical Nifty 500 equity universe (all 500 symbols including BAGMANE).
5. Performs complete DuckDB vs Parquet 5m persistence verification (timestamp sets, row counts, OHLCV values).
6. Gates production signal scan and Firebase mirroring on 100% cycle SUCCESS.
================================================================================
"""

import asyncio
import datetime
import time
import os
import sys
import json
import uuid
import duckdb
import pandas as pd
from pathlib import Path
from datetime import timezone

# Add project root to path
sys.path.append(os.getcwd())

# Ensure environment is set for local execution
os.environ["ENVIRONMENT"] = "development"

from backend.app.db.nifty500_symbols import get_nifty_500_universe
from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.services.intraday_ingestion_service import IntradayIngestionService
from backend.scripts.mirror_local_to_firestore import mirror

REDIS_LOCK_KEY = "lock:pulse"
LEASE_SECONDS = 300  # 5 minute lease

class PulseDistributedLock:
    def __init__(self, key: str = REDIS_LOCK_KEY, lease_seconds: int = LEASE_SECONDS):
        self.key = key
        self.lease_seconds = lease_seconds
        self.token = str(uuid.uuid4())
        self.redis_client = None

        try:
            import redis
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, socket_timeout=2)
            self.redis_client.ping()
        except Exception as ex:
            raise RuntimeError(f"Redis instance required for 'lock:pulse' distributed locking is unavailable: {ex}") from ex

    def acquire(self) -> bool:
        try:
            acquired = self.redis_client.set(self.key, self.token, nx=True, ex=self.lease_seconds)
            return bool(acquired)
        except Exception as ex:
            raise RuntimeError(f"Failed to acquire Redis lock '{self.key}': {ex}") from ex

    def verify_ownership(self) -> bool:
        try:
            current = self.redis_client.get(self.key)
            if current is None:
                return False
            val_str = current.decode("utf-8") if isinstance(current, bytes) else str(current)
            return val_str == self.token
        except Exception as ex:
            raise RuntimeError(f"Redis communication failure during ownership check for '{self.key}': {ex}") from ex

    def renew(self) -> bool:
        lua_renew = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        try:
            res = self.redis_client.eval(lua_renew, 1, self.key, self.token, self.lease_seconds)
            if not bool(res):
                raise RuntimeError("Redis lock renewal returned 0: lock ownership lost or key expired")
            return True
        except Exception as ex:
            raise RuntimeError(f"Redis lock renewal failed for key '{self.key}': {ex}") from ex

    def release(self) -> bool:
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            res = self.redis_client.eval(lua_script, 1, self.key, self.token)
            return bool(res)
        except Exception as ex:
            print(f"[!] Warning: Failed to release Redis lock '{self.key}': {ex}")
            return False

async def _lock_renewer_task(lock: PulseDistributedLock, lock_lost_event: asyncio.Event, interval: int = 30):
    while not lock_lost_event.is_set():
        await asyncio.sleep(interval)
        try:
            lock.renew()
        except Exception as ex:
            print(f"[!] Distributed lock lease renewal exception: {ex}")
            lock_lost_event.set()
            break

async def pulse_cycle():
    lock = PulseDistributedLock()
    if not lock.acquire():
        print("[!] Skipped pulse cycle: lock 'lock:pulse' held by active worker.")
        return

    lock_lost_event = asyncio.Event()
    renewer = asyncio.create_task(_lock_renewer_task(lock, lock_lost_event))

    print(f"\n{'='*60}")
    print(f"[*] Starting Local 5-Minute Pulse Cycle: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    try:
        # All 500 canonical symbols including BAGMANE
        symbols_dict = get_nifty_500_universe()
        all_symbols = list(symbols_dict.keys())

        print(f"[1/4] Running Intraday 5-Minute Market Data Sync across canonical universe ({len(all_symbols)} symbols)...")

        batch_size = 50
        succeeded_symbols = 0
        failed_symbols = 0
        unsupported_symbols = 0
        total_candles_persisted = 0
        latest_verified_ts = None
        symbol_details = {}

        f_dir = Path("backend/data/features")
        db_p = Path("backend/data/analytical.duckdb")

        for i in range(0, len(all_symbols), batch_size):
            if lock_lost_event.is_set() or not lock.verify_ownership():
                raise RuntimeError("Pulse cycle aborted: Redis lock 'lock:pulse' lost or lease expired mid-cycle")

            batch = all_symbols[i:i + batch_size]
            for sym in batch:
                if lock_lost_event.is_set() or not lock.verify_ownership():
                    raise RuntimeError("Pulse cycle aborted: Redis lock 'lock:pulse' lost or lease expired mid-cycle")

                try:
                    res = IntradayIngestionService.sync_symbol_5m(sym, period="1d")

                    # Verify per-symbol DuckDB vs Parquet persistence equality
                    sym_parquet = f_dir / f"{sym}_5m.parquet"
                    if not sym_parquet.exists():
                        raise RuntimeError(f"5m Parquet store missing for symbol '{sym}' after sync")

                    df_p = pd.read_parquet(sym_parquet)
                    if df_p.empty or "timestamp" not in df_p.columns:
                        raise RuntimeError(f"5m Parquet store empty or invalid for symbol '{sym}'")

                    con_v = duckdb.connect(str(db_p))
                    df_d = con_v.execute("""
                        SELECT timestamp, open as Open, high as High, low as Low, close as Close, volume as Volume
                        FROM intraday_5m_ohlcv WHERE symbol = ? ORDER BY timestamp
                    """, [sym]).df()
                    con_v.close()

                    if df_d.empty:
                        raise RuntimeError(f"5m DuckDB store empty for symbol '{sym}'")

                    p_ts = list(df_p["timestamp"])
                    d_ts = list(df_d["timestamp"])

                    if len(p_ts) != len(set(p_ts)):
                        raise RuntimeError(f"Duplicate 5m timestamps in Parquet for symbol '{sym}'")
                    if len(d_ts) != len(set(d_ts)):
                        raise RuntimeError(f"Duplicate 5m timestamps in DuckDB for symbol '{sym}'")

                    if p_ts != d_ts:
                        raise RuntimeError(f"5m timestamp set mismatch for '{sym}': Parquet {len(p_ts)} != DuckDB {len(d_ts)}")

                    if len(df_p) != res["candles_persisted"]:
                        raise RuntimeError(f"5m row count mismatch for '{sym}': Parquet {len(df_p)} != Accepted {res['candles_persisted']}")

                    # Compare OHLCV values within 1e-4 tolerance
                    p_sub = df_p.set_index("timestamp")[["Open", "High", "Low", "Close", "Volume"]].sort_index()
                    d_sub = df_d.set_index("timestamp")[["Open", "High", "Low", "Close", "Volume"]].sort_index()

                    mismatches = (
                        ((p_sub["Open"] - d_sub["Open"]).abs() > 1e-4) |
                        ((p_sub["High"] - d_sub["High"]).abs() > 1e-4) |
                        ((p_sub["Low"] - d_sub["Low"]).abs() > 1e-4) |
                        ((p_sub["Close"] - d_sub["Close"]).abs() > 1e-4) |
                        ((p_sub["Volume"] - d_sub["Volume"]).abs() > 1e-4)
                    ).sum()

                    if mismatches > 0:
                        raise RuntimeError(f"5m OHLCV value mismatch for '{sym}': {mismatches} rows exceed tolerance 1e-4")

                    # Verify ownership immediately AFTER sync and verification
                    if lock_lost_event.is_set() or not lock.verify_ownership():
                        raise RuntimeError("Pulse cycle aborted: Redis lock 'lock:pulse' lost or lease expired mid-cycle")

                    succeeded_symbols += 1
                    total_candles_persisted += res["candles_persisted"]
                    symbol_details[sym] = {"status": "SUCCESS", "latest": res["latest_timestamp"], "count": res["candles_persisted"]}
                    if not latest_verified_ts or res["latest_timestamp"] > latest_verified_ts:
                        latest_verified_ts = res["latest_timestamp"]

                except ValueError as ve:
                    if "INTRADAY_PROVIDER_UNSUPPORTED" in str(ve):
                        unsupported_symbols += 1
                        symbol_details[sym] = {"status": "UNSUPPORTED", "reason": str(ve)}
                    else:
                        failed_symbols += 1
                        symbol_details[sym] = {"status": "FAILED", "reason": str(ve)}
                except Exception as ex:
                    if "lock 'lock:pulse' lost" in str(ex):
                        raise
                    failed_symbols += 1
                    symbol_details[sym] = {"status": "FAILED", "reason": str(ex)}

        print(f"      [+] Intraday Sync Complete. Succeeded: {succeeded_symbols}, Unsupported: {unsupported_symbols}, Failed: {failed_symbols}, Total 5m Candles Persisted: {total_candles_persisted}")

        # Strict cycle status: SUCCESS requires ZERO failed and ZERO unsupported symbols
        if failed_symbols == 0 and unsupported_symbols == 0:
            cycle_status = "SUCCESS"
        elif succeeded_symbols > 0:
            cycle_status = "PARTIAL"
        else:
            cycle_status = "FAILED"

        # 2. Readback Verification from DuckDB
        print("[2/4] Verifying Persisted 5m Candles Readback from DuckDB...")
        con = duckdb.connect("backend/data/analytical.duckdb")
        duck_rows = con.execute("SELECT count(*) FROM intraday_5m_ohlcv").fetchone()[0]
        con.close()
        print(f"      [+] Readback Verified. Total 5m Candles in DuckDB: {duck_rows}")

        # 3. Production Signal Scan ONLY on complete SUCCESS
        if cycle_status == "SUCCESS":
            print("[3/4] Running Signal Scan...")
            report = await EquitySignalGenerationService.run_production_scan()
            print(f"      [+] Scan Complete. Signals: {report.get('signals_generated', 0)}, Errors: {len(report.get('errors', []))}")

            print("[4/4] Mirroring Local State to Firebase Firestore...")
            await mirror()
            print("      [+] Mirroring Successful.")
        else:
            print(f"[3/4 & 4/4] Skipping Signal Scan and Firebase Mirror due to non-SUCCESS cycle status ('{cycle_status}').")
            report = {"signals_generated": 0, "errors": [f"Market data sync status was '{cycle_status}'"]}

        # Heartbeat Update — set HEALTHY ONLY IF cycle_status == "SUCCESS"
        from backend.core.database import db_client
        if db_client:
            db_client.collection("system_metrics").document("local_pulse").set({
                "last_run": datetime.datetime.now(timezone.utc),
                "status": "HEALTHY" if cycle_status == "SUCCESS" else ("DEGRADED" if cycle_status == "PARTIAL" else "FAILED"),
                "cycle_status": cycle_status,
                "symbols_attempted": len(all_symbols),
                "symbols_succeeded": succeeded_symbols,
                "symbols_unsupported": unsupported_symbols,
                "symbols_failed": failed_symbols,
                "total_candles_persisted": total_candles_persisted,
                "latest_verified_candle_timestamp": latest_verified_ts,
                "duckdb_intraday_total_rows": duck_rows,
                "pc_identity": os.getenv("COMPUTERNAME", "Local_Workstation")
            })

    except Exception as e:
        print(f"[!] CRITICAL ERROR in Pulse Cycle: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        renewer.cancel()
        try:
            await renewer
        except asyncio.CancelledError:
            pass
        lock.release()

async def main():
    print("=== [TradeMind AI] Local Operational Pulse Worker ===")
    print("Enforcing 5-minute update interval with mandatory Redis 'lock:pulse' distributed lock.")
    print("Press CTRL+C to stop.")

    interval_seconds = 5 * 60  # 5 Minutes

    while True:
        start_time = time.time()

        try:
            await pulse_cycle()
        except Exception as ex:
            print(f"[!] Pulse cycle failed: {ex}")

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
