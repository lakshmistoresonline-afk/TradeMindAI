import os
import asyncio
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.core.container import container
from backend.services.price_resolver import PriceResolver

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

async def refresh():
    print("[*] Refreshing Active Signal Prices (V2 - Raw SQL)...")

    with engine.connect() as conn:
        # 1. Fetch Active Signal IDs and Symbols
        res = conn.execute(text("SELECT id, symbol, asset_class FROM live_signals WHERE status IN ('WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED', 'ACTIVE')"))
        signals = res.fetchall()

        print(f"   Found {len(signals)} active signals in live_signals.")

        for row in signals:
            sid, sym, asset_class = row
            print(f"   - Resolving for {sym} ({sid})...")

            # Create a dummy signal object for PriceResolver
            from backend.domain.models.ios import LiveSignal
            dummy_sig = LiveSignal(id=sid, symbol=sym, asset_class=asset_class, status="ACTIVE", direction="LONG")

            try:
                res_p = await PriceResolver.resolve_current_price(dummy_sig)
                if res_p["status"] == "FRESH":
                    price = res_p["current_price"]
                    source = res_p["source"]

                    # Update Neon
                    sql = text("""
                        UPDATE live_signals
                        SET current_price = :p,
                            current_price_timestamp = :ts,
                            current_price_source = :src,
                            current_price_status = 'FRESH'
                        WHERE id = :id
                    """)
                    conn.execute(sql, {"p": price, "ts": res_p["timestamp"], "src": source, "id": sid})
                    conn.commit()
                    print(f"     [OK] Updated: ₹{price}")
                else:
                    print(f"     [WARN] Could not resolve: {res_p['status']}")
            except Exception as e:
                print(f"     [ERR] {sym}: {e}")

if __name__ == "__main__":
    asyncio.run(refresh())
