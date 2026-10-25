import sqlite3

db_path = r"D:\TradeMindAI\backend\local_operational.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== historical_prices Source Distribution ===")
cursor.execute("SELECT source, COUNT(*) FROM historical_prices GROUP BY source;")
for r in cursor.fetchall():
    print(f"  Source: {r[0]!r:<30} Count: {r[1]:,}")

cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_prices;")
print(f"Total Unique Symbols in historical_prices: {cursor.fetchone()[0]}")

print("\n=== app_market_data Summary ===")
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT symbol) FROM app_market_data;")
r = cursor.fetchone()
print(f"Total Rows: {r[0]:,} | Unique Symbols: {r[1]}")

conn.close()
