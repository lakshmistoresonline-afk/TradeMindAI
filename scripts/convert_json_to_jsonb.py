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
    print("--- TRADEMIND AI: CONVERTING JSON COLUMNS TO JSONB ---")
    with engine.connect() as conn:
        cols = ["events", "analysis", "structured_consensus", "options_data", "financial_history", "health_metrics", "confidence_metrics"]

        # Check live_signals first
        for col in ["events"]:
             try:
                print(f"[*] Converting live_signals.{col}...")
                conn.execute(text(f"ALTER TABLE live_signals ALTER COLUMN {col} TYPE JSONB USING {col}::jsonb"))
                print(f"[+] live_signals.{col} converted.")
             except Exception as e:
                print(f"[-] Failed live_signals.{col}: {e}")

        # Check stocks
        for col in ["analysis", "structured_consensus", "options_data", "financial_history", "health_metrics", "confidence_metrics"]:
             try:
                print(f"[*] Converting stocks.{col}...")
                conn.execute(text(f"ALTER TABLE stocks ALTER COLUMN {col} TYPE JSONB USING {col}::jsonb"))
                print(f"[+] stocks.{col} converted.")
             except Exception as e:
                print(f"[-] Failed stocks.{col}: {e}")

        conn.commit()
    print("Conversion complete.")

if __name__ == "__main__":
    convert()
