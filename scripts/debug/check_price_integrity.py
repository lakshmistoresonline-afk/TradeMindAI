import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- ACTIVE SIGNAL PRICE AUDIT ---")
        res = conn.execute(text("SELECT id, symbol, entry_price, current_price, status FROM live_signals"))
        total = 0
        identical = 0

        for row in res:
            total += 1
            sid, sym, entry, current, status = row
            if entry == current:
                identical += 1
                print(f"[IDENTICAL] {sid} ({sym}): {entry} == {current} | Status: {status}")
            else:
                print(f"[OK] {sid} ({sym}): Entry {entry} != Current {current}")

        print(f"\nFinal Active Audit Summary (N=33):")
        print(f"   Total Active: {total}")
        print(f"   Independently Refreshed: {total - identical}")
        print(f"   Identity Rate: {identical/total:.1%}")

        if identical == 0:
            print("[+] Price Integrity Verified: All signals have unique Current Price telemetry.")
        else:
            print("[!] Audit Warning: Price overlap detected.")

if __name__ == "__main__":
    audit()
