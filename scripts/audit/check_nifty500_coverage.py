import sqlite3

db_path = r"D:\TradeMindAI\backend\local_operational.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT symbol FROM stocks WHERE symbol IS NOT NULL AND trim(symbol) != '';")
all_stocks = [r[0].strip() for r in c.fetchall()]

covered_stocks = []
incomplete_stocks = []

for sym in all_stocks:
    c.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol = ?;", (sym,))
    count = c.fetchone()[0]
    if count >= 1000:  # >= 1000 daily bars (~4+ years) is considered well covered
        covered_stocks.append((sym, count))
    else:
        incomplete_stocks.append((sym, count))

print(f"Total Nifty 500 Equities in stocks Table: {len(all_stocks)}")
print(f"Equities with >= 1000 Daily Bars (Full History): {len(covered_stocks)} / {len(all_stocks)} ({len(covered_stocks)/len(all_stocks)*100:.1f}%)")
print(f"Equities needing backfill (< 1000 Bars): {len(incomplete_stocks)} / {len(all_stocks)}")

if incomplete_stocks:
    print("\nSample Incomplete Equities:")
    for sym, cnt in incomplete_stocks[:15]:
        print(f"  - {sym:<20}: {cnt} bars")

conn.close()
