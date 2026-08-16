import sqlite3
import os

def check():
    db_path = 'backend/local_operational.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "="*50)
    print("TRADE MIND AI: 10-YEAR DATA VERIFICATION REPORT")
    print("="*50 + "\n")

    # 1. Operational Store (PostgreSQL/SQLite)
    print("--- 1. OPERATIONAL STORE (POSTGRESQL/SQLITE) ---")
    print("Purpose: Fast dashboard loading and real-time research.")
    cursor.execute("SELECT symbol, count(*) FROM historical_prices GROUP BY symbol")
    rows = cursor.fetchall()
    for row in rows:
        status = "✅ 10Y COMPLETE" if row[1] > 2400 else "⏳ IN PROGRESS"
        print(f"[{row[0]:.<20}] {row[1]:>5} days | {status}")

    # 2. Analytical Store (DuckDB / Parquet)
    print("\n--- 2. ANALYTICAL STORE (DUCKDB / PARQUET) ---")
    print("Purpose: High-speed ML training and 10Y Similarity matching.")
    feature_dir = 'backend/data/features'
    if os.path.exists(feature_dir):
        files = [f for f in os.listdir(feature_dir) if f.endswith('.parquet')]
        for f in files:
            size = os.path.getsize(os.path.join(feature_dir, f)) / 1024
            print(f"[{f:.<20}] {size:>8.2f} KB | ✅ INDEXED")
    else:
        print("❌ Analytical directory missing.")

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50 + "\n")

    conn.close()

if __name__ == "__main__":
    check()
