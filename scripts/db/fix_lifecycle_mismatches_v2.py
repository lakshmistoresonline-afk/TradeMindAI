import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import datetime

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

# List of symbols to transition to ACTIVE based on audit
SYMBOLS_TO_TRIGGER = [
    "CANFINHOME", "BIOCON", "BERGEPAINT", "ATGL", "ASTRAL",
    "ASIANPAINT", "APOLLOTYRE", "AMBUJACEM", "ACC", "CROMPTON",
    "COROMANDEL", "CONCOR", "BEL", "BANKBARODA", "BALKRISIND", "BHARATFORG",
    "BRITANNIA", "ASHOKLEY", "BHARTIARTL", "CGPOWER", "CUMMINSIND", "BLUEDART"
]

def fix():
    with engine.connect() as conn:
        print("=== TRADEMIND AI: FIXING LIFECYCLE MISMATCHES (V2) ===")

        # 1. Update shadow_signals
        sql = """
        UPDATE shadow_signals
        SET status = 'ACTIVE',
            lifecycle_state = 'ACTIVE',
            updated_at = :now,
            entry_timestamp = COALESCE(entry_timestamp, :now)
        WHERE symbol IN :symbols AND status = 'WAITING_FOR_ENTRY'
        """
        res = conn.execute(text(sql), {
            "now": datetime.datetime.utcnow(),
            "symbols": tuple(SYMBOLS_TO_TRIGGER)
        })
        print(f"[+] Updated {res.rowcount} records in shadow_signals.")

        # 2. Update live_signals
        sql_live = """
        UPDATE live_signals
        SET status = 'ACTIVE',
            lifecycle_state = 'ACTIVE',
            updated_at = :now,
            activated_at = COALESCE(activated_at, :now)
        WHERE symbol IN :symbols AND status = 'WAITING_FOR_ENTRY'
        """
        res_live = conn.execute(text(sql_live), {
            "now": datetime.datetime.utcnow(),
            "symbols": tuple(SYMBOLS_TO_TRIGGER)
        })
        print(f"[+] Updated {res_live.rowcount} records in live_signals.")

        conn.commit()
        print("[+] Database correction complete.")

if __name__ == "__main__":
    fix()
