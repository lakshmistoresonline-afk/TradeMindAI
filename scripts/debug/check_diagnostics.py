import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

with engine.connect() as conn:
    print("--- Diagnostic Counts ---")
    try:
        res1 = conn.execute(text("SELECT COUNT(*) FROM shadow_events"))
        print(f"shadow_events: {res1.scalar()}")
    except Exception as e: print(f"shadow_events Error: {e}")

    try:
        res2 = conn.execute(text("SELECT COUNT(*) FROM shadow_scan_diagnostics"))
        print(f"shadow_scan_diagnostics: {res2.scalar()}")
    except Exception as e: print(f"shadow_scan_diagnostics Error: {e}")

    try:
        res3 = conn.execute(text("SELECT signal_decision, COUNT(*) FROM shadow_scan_diagnostics GROUP BY signal_decision"))
        print("\nDecision Distribution (Diagnostics):")
        for row in res3: print(f"   {row[0]}: {row[1]}")
    except Exception as e: print(f"Decision Dist Error: {e}")

    print("\n--- Prediction Distribution ---")
    try:
        res4 = conn.execute(text("SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction"))
        for row in res4: print(f"   {row[0]}: {row[1]}")
    except Exception as e: print(f"Prediction Dist Error: {e}")

    print("\n--- Model Availability (Sample) ---")
    try:
        res7 = conn.execute(text("SELECT symbol, COUNT(*) FROM predictions GROUP BY symbol ORDER BY COUNT(*) ASC LIMIT 5"))
        print("Lowest Availability Symbols:")
        for row in res7: print(f"   {row[0]}: {row[1]} predictions")

        res8 = conn.execute(text("SELECT symbol, COUNT(*) FROM predictions GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 5"))
        print("\nHighest Availability Symbols:")
        for row in res8: print(f"   {row[0]}: {row[1]} predictions")
    except Exception as e: print(f"Availability Error: {e}")

    print("\n--- Regime Distribution (Shadow) ---")
    try:
        res16 = conn.execute(text("SELECT regime, COUNT(*) FROM shadow_signals GROUP BY regime"))
        for row in res16: print(f"   {row[0]}: {row[1]}")
    except Exception as e: print(f"Regime Error: {e}")
