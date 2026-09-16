import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- SAME-BAR FINAL RECONCILIATION ---")

        # 1. Fetch all terminal signals (N=50 expected)
        res = conn.execute(text("SELECT id, symbol, target_price, stop_price, outcome_timestamp, status FROM shadow_signals WHERE status != 'ACTIVE'"))
        records = res.fetchall()
        print(f"Total historical records: {len(records)}")

        verified = 0
        ambiguous = 0
        data_missing = 0

        for row in records:
            sid, sym, target, stop, out_ts, status = row
            if status == 'TIMEOUT':
                verified += 1
                continue

            if not out_ts:
                data_missing += 1
                continue

            date_str = out_ts.strftime('%Y-%m-%d')
            res_p = conn.execute(text(f"SELECT high, low FROM historical_prices WHERE symbol = '{sym}' AND date::date = '{date_str}'"))
            p_row = res_p.fetchone()

            if not p_row:
                data_missing += 1
                continue

            verified += 1
            high, low = p_row
            hit_target = high >= target if target else False
            hit_stop = low <= stop if stop else False

            if hit_target and hit_stop:
                ambiguous += 1
                print(f"   [AMBIGUOUS] {sid} ({sym}) on {date_str} - High: {high}, Low: {low}, Target: {target}, Stop: {stop}")

        print(f"\nFinal Tally:")
        print(f"   RECORDS = {len(records)}")
        print(f"   VERIFIED (PRICE DATA PRESENT) = {verified}")
        print(f"   AMBIGUOUS = {ambiguous}")
        print(f"   DATA MISSING/UNVERIFIED = {data_missing}")

        if verified > 0:
            print(f"   Ambiguity % of Verified: {ambiguous/verified:.1%}")
            print(f"   Ambiguity % of Total: {ambiguous/len(records):.1%}")

if __name__ == "__main__":
    audit()
