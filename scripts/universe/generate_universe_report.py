import os
import sys
import json
from sqlalchemy import text
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

REPORT_MD = "docs/NIFTY200_UNIVERSE_COVERAGE_REPORT.md"
REPORT_JSON = "validation/results/universe_coverage.json"
EXPECTED_START_DATE = datetime(2020, 1, 1)

def generate_report():
    print("[*] Generating NIFTY 200 Universe/Data Coverage Report...")

    canonical_symbols = set(NIFTY_200_CONSTITUENTS)

    try:
        with engine.connect() as conn:
            # Fetch aggregate stats for all symbols in history
            query = text("""
                SELECT symbol,
                       min(date) as first_candle,
                       max(date) as last_candle,
                       count(*) as candle_count
                FROM historical_prices
                GROUP BY symbol
            """)
            res = conn.execute(query).fetchall()
            db_stats = {r[0]: {"first": r[1], "last": r[2], "count": r[3]} for r in res}

            report_data = []

            for symbol in sorted(list(canonical_symbols)):
                stats = db_stats.get(symbol)

                if stats:
                    first = stats["first"]
                    last = stats["last"]
                    count = stats["count"]

                    # Ensure first is datetime object for comparison
                    if isinstance(first, str):
                        try:
                            first = datetime.fromisoformat(first.split('.')[0])
                        except:
                            first = None

                    # Coverage calculation
                    total_days = (datetime.now() - EXPECTED_START_DATE).days
                    expected_candles = (total_days / 365) * 252
                    coverage_pct = min(100.0, (count / expected_candles) * 100) if expected_candles > 0 else 0

                    limitation = "NONE"
                    if first and first > EXPECTED_START_DATE.replace(year=EXPECTED_START_DATE.year + 1):
                        limitation = "RECENT_LISTING"

                    report_data.append({
                        "symbol": symbol,
                        "canonical_status": "PASS",
                        "first_candle": first.strftime('%Y-%m-%d') if first else "-",
                        "last_candle": last.strftime('%Y-%m-%d') if isinstance(last, datetime) else str(last),
                        "candle_count": count,
                        "expected_history_start": EXPECTED_START_DATE.strftime('%Y-%m-%d'),
                        "actual_history_start": first.strftime('%Y-%m-%d') if first else "-",
                        "coverage_percentage": round(coverage_pct, 2),
                        "listing_limitation": limitation,
                        "provider_limitation": "NONE" if count > 0 else "DATA_MISSING",
                        "validation_eligibility": "ELIGIBLE" if count > 100 else "INELIGIBLE"
                    })
                else:
                    report_data.append({
                        "symbol": symbol,
                        "canonical_status": "PASS",
                        "first_candle": "-",
                        "last_candle": "-",
                        "candle_count": 0,
                        "expected_history_start": EXPECTED_START_DATE.strftime('%Y-%m-%d'),
                        "actual_history_start": "-",
                        "coverage_percentage": 0.0,
                        "listing_limitation": "UNKNOWN",
                        "provider_limitation": "DATA_UNAVAILABLE",
                        "validation_eligibility": "INELIGIBLE"
                    })

            # Output Markdown Table Manually
            os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
            with open(REPORT_MD, "w") as f:
                f.write("# NIFTY 200 Universe Coverage Report\n\n")
                f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                headers = ["Symbol", "Status", "First", "Last", "Rows", "Start", "Coverage %", "Limitation", "Eligibility"]
                f.write("| " + " | ".join(headers) + " |\n")
                f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

                for row in report_data:
                    line = [
                        row["symbol"],
                        row["canonical_status"],
                        row["first_candle"],
                        row["last_candle"],
                        str(row["candle_count"]),
                        row["actual_history_start"],
                        f"{row['coverage_percentage']}%",
                        row["listing_limitation"],
                        row["validation_eligibility"]
                    ]
                    f.write("| " + " | ".join(line) + " |\n")

            # Output JSON
            os.makedirs(os.path.dirname(REPORT_JSON), exist_ok=True)
            with open(REPORT_JSON, "w") as f:
                json.dump(report_data, f, indent=4, default=str)

            print(f"[SUCCESS] Reports generated: {REPORT_MD}, {REPORT_JSON}")

    except Exception as e:
        print(f"[!] Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    generate_report()
