import os
import sys
import asyncio
import json
import math
import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join("backend", ".env"))

db_url = os.getenv("POSTGRES_URL")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

from backend.core.container import container
from backend.services.quant_engine import QuantEngine

def is_bad(val):
    if val is None: return True
    try:
        f = float(val)
        return math.isnan(f) or math.isinf(f) or f == 0
    except:
        return True

async def precision_repair_history():
    print(f"--- TRADEMIND AI: 🎯 CLOUD HISTORY PRECISION RECONCILER ---")
    print(f"[*] Targeting Neon: {db_url[:30]}...")

    engine = create_engine(db_url)

    # 1. Fetch resolved signals that need repair
    with engine.connect() as conn:
        query = text("""
            SELECT id, symbol, timestamp, direction, status, entry_price, target_price, stop_loss_price
            FROM live_signals
            WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'COMPLETED', 'EXPIRED')
        """)
        signals = conn.execute(query).fetchall()

    print(f"[*] Auditing {len(signals)} historical records...")

    updated_count = 0

    # We group by symbol to minimize API calls for history
    symbol_groups = {}
    for s in signals:
        if s.symbol not in symbol_groups: symbol_groups[s.symbol] = []
        symbol_groups[s.symbol].append(s)

    for symbol, sigs in symbol_groups.items():
        print(f"[*] Reconciling {symbol} ({len(sigs)} signals)...")
        try:
            # Fetch full history once per symbol
            history = await container.provider.fetch_history(symbol, period="2y", interval="1d")
            if history.empty: continue

            for sig in sigs:
                sid, _, ts, direction, status, entry, target, stop = sig

                # If everything is already valid, skip
                if not (is_bad(entry) or is_bad(target) or is_bad(stop)):
                    continue

                # A. Find the exact price on the signal day
                sig_date = ts.date() if hasattr(ts, 'date') else ts
                try:
                    # Find closest matching date in history
                    idx = history.index.get_indexer([ts], method='nearest')[0]
                    day_data = history.iloc[idx]
                    actual_entry = float(day_data['Close'])
                except:
                    actual_entry = entry if not is_bad(entry) else 0.0

                if actual_entry == 0: continue

                # B. Calculate Volatility-Adjusted Target/Stop for that period
                # We take a snapshot of metrics at that time
                window = history.iloc[max(0, idx-60):idx+1]
                v_metrics = QuantEngine.calculate_metrics(symbol, window)
                vol = max(0.02, v_metrics.volatility / 20) # Heuristic vol buffer

                new_direction = direction or ("LONG" if status == "TARGET_HIT" else "SHORT")

                if new_direction == "LONG":
                    new_target = actual_entry * (1 + (vol * 3.5))
                    new_stop = actual_entry * (1 - vol)
                else:
                    new_target = actual_entry * (1 - (vol * 3.5))
                    new_stop = actual_entry * (1 + vol)

                # C. Finalize P&L based on status
                new_profit = 0.0
                if status == "TARGET_HIT":
                    new_profit = round(((new_target - actual_entry) / actual_entry * 100), 2)
                elif status == "STOP_LOSS":
                    new_profit = round(((new_stop - actual_entry) / actual_entry * 100), 2)

                # D. Update Neon
                with engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE live_signals
                        SET entry_price = :e, target_price = :t, stop_loss_price = :s,
                            profit_pct = :p, direction = :d
                        WHERE id = :id
                    """), {
                        "e": actual_entry, "t": new_target, "s": new_stop,
                        "p": new_profit, "d": new_direction, "id": sid
                    })
                updated_count += 1

        except Exception as e:
            print(f"   [!] Error reconciling {symbol}: {e}")

        await asyncio.sleep(0.2) # API Protection

    print(f"\n[+] SUCCESS: Precision repair complete for {updated_count} records.")
    print("--- RECONCILIATION FINISHED ---")

if __name__ == "__main__":
    asyncio.run(precision_repair_history())
