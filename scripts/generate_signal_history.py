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
    print("--- TRADEMIND AI: SIGNAL HISTORY GENERATOR ---")
    print("[*] Performing Forensic Audit of Historical Setups...")

    # Target missing leaders for final population
    symbols = ["RELIANCE", "INFY"]

    engine = BacktestEngine(db_client)

    for symbol in symbols:
        print(f"\n[*] Auditing {symbol}...")
        try:
            # Generate history for last 1 year to show recent relevance
            report = engine.run_10y_backtest(symbol, period="1y")
            if "error" in report:
                print(f"   [!] {report['error']}")
                continue

            print(f"   [+] Audit Complete: {report.get('total_signals', 0)} signals | {report.get('success_rate', 0):.1f}% Win Rate")

            # Extended cooldown for high-density analysis
            await asyncio.sleep(30)
        except Exception as e:
            print(f"   [!] Error auditing {symbol}: {e}")

    print("\n--- SIGNAL HISTORY POPULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
