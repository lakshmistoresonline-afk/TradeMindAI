import sqlite3
import os

db_path = r"D:\TradeMindAI\backend\local_operational.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== LiveSignalDB (live_signals) Summary ===")
cursor.execute("SELECT symbol, direction, rating, entry_price, target_price, stop_price, status, created_at FROM live_signals;")
live_rows = cursor.fetchall()

if not live_rows:
    print("  Live Signals Table: 0 Active Signals (Quarantine / Fail-Closed Active)")
else:
    print(f"  Total Live Signals: {len(live_rows)}")
    for r in live_rows:
        print(f"    - Symbol: {r[0]:<12} Direction: {r[1]} Rating: {r[2]} Entry: ₹{r[3]} Target: ₹{r[4]} Stop: ₹{r[5]} Status: {r[6]} Created: {r[7]}")

print("\n=== ShadowSignalDB (shadow_signals) Summary ===")
cursor.execute("SELECT symbol, COUNT(*) FROM shadow_signals GROUP BY symbol ORDER BY COUNT(*) DESC;")
shadow_counts = cursor.fetchall()

cursor.execute("SELECT COUNT(*) FROM shadow_signals;")
total_shadow = cursor.fetchone()[0]

print(f"  Total Historical Replay Signals in shadow_signals: {total_shadow}")
if shadow_counts:
    print("  Per-Stock Historical Signal Breakdown:")
    for sym, cnt in shadow_counts:
        print(f"    - {sym:<15}: {cnt} historical signals")

conn.close()
