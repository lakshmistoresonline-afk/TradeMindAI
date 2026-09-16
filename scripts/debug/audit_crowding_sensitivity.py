import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def calculate_metrics(df):
    if df.empty:
        return {"win_rate": 0, "expectancy": 0, "pf": 0, "count": 0}

    total = len(df)
    wins = len(df[df['status'] == 'TARGET_HIT'])
    losses = len(df[df['status'] == 'STOP_LOSS'])
    win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0

    # Simple PF: sum(abs(wins)) / sum(abs(losses))
    # We'll use net_pnl column if available, otherwise assume fixed R:R
    # Strategy V2.2 uses 1:2.5 (Swing) and 1:2.0 (Short)

    returns = df['net_return'].dropna().tolist()
    if not returns:
        return {"win_rate": win_rate, "count": total}

    avg_win = sum([r for r in returns if r > 0]) / wins if wins > 0 else 0
    avg_loss = abs(sum([r for r in returns if r < 0]) / losses) if losses > 0 else 1
    pf = (wins * avg_win) / (losses * avg_loss) if (losses * avg_loss) > 0 else float('inf')
    expectancy = sum(returns) / total

    return {
        "count": total,
        "win_rate": round(win_rate, 2),
        "pf": round(pf, 2),
        "expectancy": round(expectancy, 4)
    }

def audit():
    with engine.connect() as conn:
        print("--- CROWDING SENSITIVITY AUDIT ---")

        sql = "SELECT id, symbol, timestamp::date as date, status, net_return FROM shadow_signals WHERE status != 'ACTIVE'"
        df = pd.read_sql(sql, conn)

        print(f"Full Population: {calculate_metrics(df)}")

        # Exclude Aug 24
        df_no_aug24 = df[df['date'].astype(str) != '2026-08-24']
        print(f"Exclude 2026-08-24: {calculate_metrics(df_no_aug24)}")

        # Exclude Sep 09
        df_no_sep09 = df[df['date'].astype(str) != '2026-09-09']
        print(f"Exclude 2026-09-09: {calculate_metrics(df_no_sep09)}")

        # Exclude both
        df_no_both = df[(df['date'].astype(str) != '2026-08-24') & (df['date'].astype(str) != '2026-09-09')]
        print(f"Exclude Both: {calculate_metrics(df_no_both)}")

if __name__ == "__main__":
    audit()
