import sqlite3
conn = sqlite3.connect('backend/local_operational.db')
print('NIFTY:', conn.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol='NIFTY'").fetchone()[0])
print('^NSEI:', conn.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol='^NSEI'").fetchone()[0])
print('RELIANCE:', conn.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol='RELIANCE'").fetchone()[0])
conn.close()
