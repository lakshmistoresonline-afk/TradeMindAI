import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- SAME-BAR AMBIGUITY AUDIT ---")

        # 1. Fetch resolved signals with target/stop outcome in status or outcome column
        res = conn.execute(text("SELECT id, symbol, target_price, stop_price, outcome_timestamp, status FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS')"))
        ambiguous_count = 0
        total_checked = 0

        for row in res:
            sid, sym, target, stop, out_ts, outcome = row
            if not out_ts: continue

            # 2. Get OHLC for that day
            # date in historical_prices is timestamp
            date_str = out_ts.strftime('%Y-%m-%d')
            res_p = conn.execute(text(f"SELECT high, low FROM historical_prices WHERE symbol = '{sym}' AND date::date = '{date_str}'"))
            p_row = res_p.fetchone()

            if p_row:
                total_checked += 1
                high, low = p_row
                hit_target = high >= target if target else False
                hit_stop = low <= stop if stop else False

                if hit_target and hit_stop:
                    ambiguous_count += 1
                    print(f"Ambiguous: {sid} ({sym}) on {date_str} - High: {high}, Low: {low}, Target: {target}, Stop: {stop}")

        print(f"\nTotal Resolved Checked: {total_checked}")
        print(f"Ambiguous Same-Bar Events: {ambiguous_count}")
        if total_checked > 0:
            print(f"Ambiguity Rate: {ambiguous_count/total_checked:.1%}")

if __name__ == "__main__":
    audit()
