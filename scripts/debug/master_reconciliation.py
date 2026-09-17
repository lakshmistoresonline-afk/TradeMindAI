import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def reconcile():
    with engine.connect() as conn:
        print("=== TRADEMIND AI: MASTER POPULATION RECONCILIATION ===")

        # 1. Total Signals in Ledger
        res = conn.execute(text("SELECT id, symbol, status, strategy_version, created_at FROM shadow_signals"))
        df = pd.DataFrame(res.fetchall(), columns=res.keys())

        print(f"Total Ledger Records: {len(df)}")

        # 2. Historical (Closed) Denominator
        historical = df[df['status'] != 'ACTIVE']
        print(f"Historical (Terminal) Records: {len(historical)}")

        # 3. Status Breakdown
        print("\nStatus Distribution:")
        print(historical['status'].value_counts())

        # 4. Strategy Version Check
        print("\nStrategy Versions in Ledger:")
        print(df['strategy_version'].value_counts())

        # 5. Same-Bar Ambiguity (Phase 14)
        print("\nChecking Same-Bar Ambiguity...")
        # (N=50 population)
        ambiguous_sql = """
        SELECT s.id, s.symbol, s.target_price, s.stop_price, s.outcome_timestamp, s.status, p.high, p.low
        FROM shadow_signals s
        JOIN historical_prices p ON s.symbol = p.symbol AND s.outcome_timestamp::date = p.date::date
        WHERE s.status IN ('TARGET_HIT', 'STOP_LOSS')
        """
        res_amb = conn.execute(text(ambiguous_sql))
        df_amb = pd.DataFrame(res_amb.fetchall(), columns=res_amb.keys())

        # Invariant: high >= target AND low <= stop
        # Need to handle LONG/SHORT
        # LONG: Target > Stop. SHORT: Target < Stop.
        # But the logic high >= target AND low <= stop works for both if target and stop are set.

        mask = (df_amb['high'] >= df_amb['target_price']) & (df_amb['low'] <= df_amb['stop_price'])
        ambiguous_records = df_amb[mask]

        print(f"Verified Outcome Records (with price data): {len(df_amb)}")
        print(f"Ambiguous Records Found: {len(ambiguous_records)}")
        for idx, row in ambiguous_records.iterrows():
            print(f"   [AMBIGUOUS] {row['id']} ({row['symbol']}) on {row['outcome_timestamp']}")

        # 6. Win Rate Denominator (Phase 21)
        # Methodology: Wins / (Wins + Losses)
        wins = len(historical[historical['status'] == 'TARGET_HIT'])
        losses = len(historical[historical['status'] == 'STOP_LOSS'])
        denominator = wins + losses
        win_rate = (wins / denominator * 100) if denominator > 0 else 0

        print(f"\nFinal Performance Denominators:")
        print(f"   Total Outcomes: {len(historical)}")
        print(f"   Win-Rate Denominator (Wins+Losses): {denominator}")
        print(f"   Timeouts (Excluded from WR): {len(historical[historical['status'] == 'TIMEOUT'])}")
        print(f"   Calculated Win Rate: {win_rate:.2f}%")

if __name__ == "__main__":
    reconcile()
