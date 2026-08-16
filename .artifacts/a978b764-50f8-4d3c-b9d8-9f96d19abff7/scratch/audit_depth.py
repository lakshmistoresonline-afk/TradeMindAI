import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def audit():
    with engine.connect() as conn:
        print("[*] Auditing historical depth...")
        query = text("""
            SELECT symbol, min(date) as first_date, max(date) as last_date, count(*) as c
            FROM historical_prices
            GROUP BY symbol
        """)
        df = pd.read_sql(query, conn)

        if df.empty:
            print("[!] No data found in historical_prices.")
            return

        df['first_date'] = pd.to_datetime(df['first_date'])

        stats = {
            "Total Stocks": len(df),
            "Earliest Overall": df['first_date'].min(),
            "Latest Overall": df['last_date'].max(),
            "Avg Candles": df['c'].mean(),
            "Stocks starting 2020 or before": len(df[df['first_date'] <= '2020-12-31']),
            "Stocks starting 2021": len(df[(df['first_date'] >= '2021-01-01') & (df['first_date'] <= '2021-12-31')]),
            "Stocks starting 2022": len(df[(df['first_date'] >= '2022-01-01') & (df['first_date'] <= '2022-12-31')]),
            "Stocks starting 2023": len(df[(df['first_date'] >= '2023-01-01') & (df['first_date'] <= '2023-12-31')]),
            "Stocks starting 2024": len(df[(df['first_date'] >= '2024-01-01') & (df['first_date'] <= '2024-12-31')]),
            "Stocks starting 2025+": len(df[df['first_date'] >= '2025-01-01'])
        }

        print("\n--- Depth Distribution ---")
        for k, v in stats.items():
            print(f"{k}: {v}")

        # Write MD report
        report_path = "docs/HISTORICAL_DEPTH_AUDIT.md"
        with open(report_path, "w") as f:
            f.write("# Historical Data Depth Audit\n\n")
            f.write(f"**Audit Timestamp**: {datetime.utcnow()} UTC\n\n")
            f.write("## 1. Distribution Summary\n\n")
            f.write("| Metric | Value |\n")
            f.write("| :--- | :--- |\n")
            for k, v in stats.items():
                f.write(f"| {k} | {v} |\n")

            f.write("\n## 2. Per-Stock Earliest Dates (Sample)\n\n")
            f.write(df.sort_values('first_date').head(20).to_markdown(index=False))

if __name__ == "__main__":
    audit()
