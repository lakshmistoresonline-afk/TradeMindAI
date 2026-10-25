import asyncio
import datetime
import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.services.signal_engine import SignalEngine

async def scan_history():
    symbols = ['TRENT', 'BEL', 'HAL', 'RELIANCE', 'TCS', 'INFY', 'ICICIBANK', 'BHARTIARTL', 'PERSISTENT', 'DIXON']
    start_dt = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)

    dates = [start_dt + datetime.timedelta(days=i) for i in range(0, 365, 5)]

    signals_count = 0
    for sym in symbols:
        for d in dates:
            sig = await SignalEngine.generate_signal(sym, 'EQUITY', 'SWING', evaluation_timestamp=d)
            if sig:
                signals_count += 1
                dt_str = d.strftime('%Y-%m-%d')
                print(f"[+] BUY SIGNAL: {sym:<12} Date: {dt_str} Entry: ₹{sig.entry_price:.2f} Target: ₹{sig.target_price:.2f} Stop: ₹{sig.stop_price:.2f}")

    print(f"\nTotal historical BUY signals generated across test: {signals_count}")

if __name__ == "__main__":
    asyncio.run(scan_history())
