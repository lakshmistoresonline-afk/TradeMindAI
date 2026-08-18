
import os
import sys
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def generate_daily_report():
    today = datetime.utcnow().date()
    print(f"--- GENERATING DAILY PRODUCTION REPORT: {today} ---")

    with engine.connect() as conn:
        # 1. Scanning Stats
        # (Assuming we log scans in a separate table, but for now we look at shadow_signals)
        query = text(f"SELECT count(*) FROM shadow_signals WHERE date(timestamp) = '{today}'")
        signal_count = conn.execute(query).scalar()

        # 2. Realized Results Today
        query_res = text(f"SELECT status, net_return, symbol FROM shadow_signals WHERE date(outcome_timestamp) = '{today}'")
        df_res = pd.read_sql(query_res, conn)

        # 3. Open Positions
        query_open = text("SELECT symbol, direction, entry_price, status FROM shadow_signals WHERE status = 'ACTIVE'")
        df_open = pd.read_sql(query_open, conn)

        # 4. System Health (Price Staleness)
        query_fresh = text("SELECT symbol, max(date) as last_date FROM historical_prices GROUP BY symbol")
        df_fresh = pd.read_sql(query_fresh, conn)
        df_fresh['age'] = (datetime.utcnow() - pd.to_datetime(df_fresh['last_date'])).dt.total_seconds() / 3600
        stale_count = (df_fresh['age'] > 24).sum()

    # Build Markdown
    report_path = f"production/reports/DAILY_REPORT_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Production Report: {today}\n\n")

        f.write("## 1. Execution Summary\n")
        f.write(f"- **Signals Generated**: {signal_count}\n")
        f.write(f"- **Realized Trades**: {len(df_res)}\n")
        f.write(f"- **Open Positions**: {len(df_open)}\n\n")

        if not df_res.empty:
            f.write("## 2. Realized Performance\n")
            f.write(df_res.to_markdown(index=False) + "\n\n")

        f.write("## 3. System Health\n")
        f.write(f"- **Stale Assets (>24h)**: {stale_count} / {len(df_fresh)}\n")
        f.write(f"- **Gating Status**: {'OPERATIONAL' if stale_count < 10 else 'DEGRADED'}\n")

    print(f"[SUCCESS] Report generated: {report_path}")

if __name__ == "__main__":
    generate_daily_report()
