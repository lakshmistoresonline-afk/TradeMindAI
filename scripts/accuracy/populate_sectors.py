import os
import sys
import asyncio
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

async def populate_missing_sectors():
    print("[*] Starting sector population for missing symbols...")
    conn = sqlite3.connect('backend/local_operational.db')
    cursor = conn.cursor()

    # Identify symbols with missing sectors
    df_missing = pd.read_sql_query("SELECT symbol FROM stocks WHERE sector IS NULL OR sector = 'Unknown'", conn)
    symbols = df_missing['symbol'].tolist()[:20]

    if not symbols:
        print("[+] No missing sectors found.")
        conn.close()
        return

    print(f"[*] Found {len(symbols)} symbols needing sector data.")

    # Mapping for Yahoo Finance symbols
    mapping = {
        "GMRINFRA": "GMRAIRPORT.NS",
        "L&TFH": "LTF.NS",
        "TATAMOTORS": "TATAMOTORS.NS", # Ensure standard
        "ZOMATO": "ZOMATO.NS",
        "PEL": "PEL.NS"
    }

    count = 0
    for sym in symbols:
        try:
            yf_sym = mapping.get(sym.upper(), f"{sym.upper()}.NS")
            ticker = yf.Ticker(yf_sym)
            info = ticker.info

            sector = info.get('sector')
            industry = info.get('industry')

            if sector:
                cursor.execute(
                    "UPDATE stocks SET sector = ?, industry = ?, updated_at = ? WHERE symbol = ?",
                    (sector, industry, datetime.utcnow().isoformat(), sym)
                )
                count += 1
                print(f"   [+] Updated {sym}: {sector}")
            else:
                print(f"   [!] No sector found for {sym}")

        except Exception as e:
            print(f"   [!] Error fetching {sym}: {e}")

        if count % 10 == 0 and count > 0:
            conn.commit()

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Sector population complete. {count} symbols updated.")

if __name__ == "__main__":
    asyncio.run(populate_missing_sectors())
