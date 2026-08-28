import os
import sys
import asyncio
import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.analysis.backtester import BacktestEngine
from backend.core.database import db_client

async def main():
    print("--- TRADEMIND AI: RESUMING SIGNAL HISTORY GENERATION ---")

    symbols = ["TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "AXISBANK", "LT", "ITC"]

    engine = BacktestEngine(db_client)

    for symbol in symbols:
        # Check if already has enough signals
        bt_ref = db_client.collection("backtests").document(symbol)
        bt_doc = bt_ref.get()
        if bt_doc.exists and bt_doc.to_dict().get("total_signals", 0) >= 3:
            print(f"[*] Skipping {symbol} (Already has {bt_doc.to_dict().get('total_signals')} signals)")
            continue

        print(f"\n[*] Deep Auditing {symbol}...")
        try:
            report = engine.run_10y_backtest(symbol, period="6mo")
            if "error" in report:
                print(f"   [!] {report['error']}")
                continue
            print(f"   [+] Audit Complete: {report.get('total_signals', 0)} signals | {report.get('success_rate', 0):.1f}% Win Rate")
            await asyncio.sleep(20) # Conservative cooldown
        except Exception as e:
            print(f"   [!] Error auditing {symbol}: {e}")

    print("\n--- SIGNAL POPULATION RESUME COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
