import sqlalchemy
from sqlalchemy import text, create_engine
import os
import json
from datetime import datetime

# Database URLs
neon_url = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
local_url = "sqlite:///G:/TradeMindAI/backend/local_operational.db"

def sync():
    print("=== [TradeMind AI] Production to Local Database Sync ===")

    neon_engine = create_engine(neon_url)
    local_engine = create_engine(local_url)

    tables = ["stocks", "model_registry", "live_signals", "shadow_signals", "historical_prices"]

    with neon_engine.connect() as neon_conn, local_engine.connect() as local_conn:
        for table in tables:
            print(f"[*] Syncing table: {table}...")
            try:
                # 1. Fetch from Neon
                res = neon_conn.execute(text(f"SELECT * FROM {table}"))
                rows = [dict(r._mapping) for r in res]
                print(f"   - Found {len(rows)} records in Neon.")

                if not rows:
                    continue

                # 2. Insert into Local (Upsert logic)
                # For SQLite, we'll use a simple INSERT OR REPLACE if possible,
                # or just clean and insert for master data.

                # Get columns for this table in local
                col_res = local_conn.execute(text(f"PRAGMA table_info({table})"))
                local_cols = [r[1] for r in col_res.fetchall()]

                # Filter rows to match local columns
                valid_rows = []
                for row in rows:
                    clean_row = {k: v for k, v in row.items() if k in local_cols}
                    # Handle JSON types for SQLite (convert dict/list to string if needed)
                    for k, v in clean_row.items():
                        if isinstance(v, (dict, list)):
                            clean_row[k] = json.dumps(v)
                    valid_rows.append(clean_row)

                # Perform chunked insert to avoid SQL length limits
                chunk_size = 50
                for i in range(0, len(valid_rows), chunk_size):
                    chunk = valid_rows[i:i + chunk_size]

                    # Prepare SQL
                    placeholders = ", ".join([f":{k}" for k in chunk[0].keys()])
                    cols = ", ".join(chunk[0].keys())

                    # Using INSERT OR REPLACE for unique constraint handling
                    sql = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})"
                    local_conn.execute(text(sql), chunk)

                local_conn.commit()
                print(f"   [+] Successfully synced {len(valid_rows)} records to Local.")

            except Exception as e:
                print(f"   [!] Error syncing {table}: {e}")

    print("\n=== Sync Complete. Local Database is now up to date with Production. ===")

if __name__ == "__main__":
    sync()
