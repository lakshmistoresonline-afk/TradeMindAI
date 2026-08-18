
import os
import sqlite3
import pandas as pd

def stats():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)

    try:
        # Check NO_TRADE reasons from logs - wait, signal_engine.py PRINTS rejections but doesn't persist them to DB
        # Only persistent signals are in shadow_signals.

        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM shadow_signals")
        signals = cursor.fetchone()[0]
        print(f"Total Persistent Shadow Signals: {signals}")

        # Check model coverage from registry again
        cursor.execute("SELECT count(*) FROM model_registry WHERE is_champion = 1")
        champions = cursor.fetchone()[0]
        print(f"Registered Champion Models: {champions}")

    finally:
        conn.close()

if __name__ == "__main__":
    stats()
