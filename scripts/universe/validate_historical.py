import os
import sys
import json
from sqlalchemy import text
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine, DATABASE_URL
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

REPORT_FILE = "docs/NIFTY200_HISTORICAL_COVERAGE_REPORT.md"
EXPECTED_START_DATE = datetime(2020, 1, 1)

def validate():
    print("============================================================")
    print(" NIFTY 200 HISTORICAL DATA VALIDATION")
    print(f" TARGET DB: {DATABASE_URL}")
    print("============================================================")

    expected_symbols = set(NIFTY_200_CONSTITUENTS)
    expected_count = len(expected_symbols)

    report_data = []

    try:
        with engine.connect() as conn:
            # 1. Fetch aggregate stats for all symbols
            query = text("""
                SELECT symbol,
                       min(date) as first_date,
                       max(date) as last_date,
                       count(*) as row_count
                FROM historical_prices
                GROUP BY symbol
            """)
            res = conn.execute(query).fetchall()

            db_stats = {r[0]: {"first": r[1], "last": r[2], "count": r[3]} for r in res}

            complete_count = 0
            partial_count = 0
            missing_count = 0

            for symbol in sorted(list(expected_symbols)):
                stats = db_stats.get(symbol)

                status = "FAILED"
                error = ""

                if stats:
                    row_count = stats["count"]
                    first = stats["first"]

                    if isinstance(first, str):
                        try: first = datetime.fromisoformat(first.split('.')[0])
                        except: first = None

                    # Coverage calculation
                    total_days = (datetime.now() - EXPECTED_START_DATE).days
                    expected_candles = (total_days / 365) * 252
                    coverage_pct = min(100.0, (row_count / expected_candles) * 100) if expected_candles > 0 else 0

                    if row_count >= 1000:
                        status = "COMPLETE"
                        complete_count += 1
                    elif symbol in ["GUJGASLTD", "TATAMOTORS", "PEL", "GMRINFRA", "L&TFH", "ZOMATO", "DELHIVERY", "NYKAA", "PAYTM", "LICI"]:
                        status = "VALID_SHORT_HISTORY"
                        complete_count += 1
                    else:
                        status = "PARTIAL"
                        partial_count += 1
                        error = f"Insufficient history ({row_count} rows, {round(coverage_pct, 1)}% coverage)."
                else:
                    status = "DATA_UNAVAILABLE"
                    missing_count += 1
                    error = "No candles found in database."

                report_data.append({
                    "Symbol": symbol,
                    "First Date": str(stats["first"]) if stats else "-",
                    "Last Date": str(stats["last"]) if stats else "-",
                    "Rows": stats["count"] if stats else 0,
                    "Status": status,
                    "Error": error
                })

            # Overall Stats
            print(f"Expected stocks: {expected_count}")
            print(f"Valid histories: {complete_count}")
            print(f"Partial stocks: {partial_count}")
            print(f"Data unavailable: {missing_count}")

            # 2. Write Report (Manual Markdown Table)
            os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
            with open(REPORT_FILE, "w") as f:
                f.write("# NIFTY 200 Historical Coverage Report\n\n")
                f.write(f"**Last Validated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
                f.write("## 1. Summary\n\n")
                f.write(f"| Metric | Value |\n")
                f.write(f"| :--- | :--- |\n")
                f.write(f"| Expected Stocks | {expected_count} |\n")
                f.write(f"| Valid Histories (Incl. Short) | {complete_count} |\n")
                f.write(f"| Partial Stocks | {partial_count} |\n")
                f.write(f"| Data Unavailable | {missing_count} |\n\n")

                f.write("## 2. Detailed Coverage\n\n")
                headers = ["Symbol", "First Date", "Last Date", "Rows", "Status", "Error"]
                f.write("| " + " | ".join(headers) + " |\n")
                f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                for r in report_data:
                    line = [r["Symbol"], r["First Date"], r["Last Date"], str(r["Rows"]), r["Status"], r["Error"]]
                    f.write("| " + " | ".join(line) + " |\n")

            print(f"\n[SUCCESS] Report generated: {REPORT_FILE}")

            # GATE: Pass if at least 198/200 are available
            if missing_count > 2:
                print(f"\nSTATUS: FAIL ({missing_count} stocks missing data)")
                sys.exit(1)
            elif missing_count > 0:
                print(f"\nSTATUS: PASS (PARTIAL - {missing_count} stocks DATA_UNAVAILABLE)")
                sys.exit(0)
            else:
                print("\nSTATUS: PASS")
                sys.exit(0)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    validate()
