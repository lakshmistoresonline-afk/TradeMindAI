import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def convert():
    print("--- TRADEMIND AI: CONVERTING JSON COLUMNS TO TEXT (OID 114 FIX) ---")
    with engine.connect() as conn:
        # Table: live_signals
        for col in ["events"]:
             try:
                print(f"[*] Converting live_signals.{col} to TEXT...")
                conn.execute(text(f"ALTER TABLE live_signals ALTER COLUMN {col} TYPE TEXT USING {col}::text"))
                print(f"[+] live_signals.{col} converted.")
             except Exception as e:
                print(f"[-] Failed live_signals.{col}: {e}")

        # Table: stocks
        for col in ["analysis", "structured_consensus", "options_data", "financial_history", "health_metrics", "confidence_metrics"]:
             try:
                print(f"[*] Converting stocks.{col} to TEXT...")
                conn.execute(text(f"ALTER TABLE stocks ALTER COLUMN {col} TYPE TEXT USING {col}::text"))
                print(f"[+] stocks.{col} converted.")
             except Exception as e:
                print(f"[-] Failed stocks.{col}: {e}")

        # Table: historical_prices
        try:
            print("[*] Converting historical_prices.indicators to TEXT...")
            conn.execute(text("ALTER TABLE historical_prices ALTER COLUMN indicators TYPE TEXT USING indicators::text"))
        except: pass

        # Table: feature_definitions
        for col in ["dependencies", "lineage"]:
            try: conn.execute(text(f"ALTER TABLE feature_definitions ALTER COLUMN {col} TYPE TEXT USING {col}::text"))
            except: pass

        conn.commit()
    print("Database conversion to TEXT complete.")

if __name__ == "__main__":
    convert()
