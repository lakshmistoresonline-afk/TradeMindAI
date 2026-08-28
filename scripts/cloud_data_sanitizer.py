import os
import sys
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

def sanitize_value(val, fallback=0.0):
    if val is None: return fallback
    try:
        f_val = float(val)
        if math.isnan(f_val) or math.isinf(f_val):
            return fallback
        return f_val
    except:
        return fallback

def run_sanitization():
    print(f"--- TRADEMIND AI: 🛡️ CLOUD DATA SANITIZER ---")
    engine = create_engine(db_url)

    with engine.begin() as conn:
        print("[*] Fetching all signals...")
        # 1. Sanitize Live Signals Table
        signals = conn.execute(text("SELECT id, symbol, entry_price, target_price, stop_loss_price, rating FROM live_signals")).fetchall()

        updated_count = 0
        for sig in signals:
            sid, symbol, entry, target, stop, rating = sig

            new_entry = sanitize_value(entry)
            if new_entry == 0:
                # Try to fetch last price from stocks table if entry is missing
                res = conn.execute(text("SELECT last_price FROM stocks WHERE symbol = :s"), {"s": symbol}).fetchone()
                if res and res[0]:
                    new_entry = sanitize_value(res[0])

            # Heuristic repair for missing targets/stops
            new_target = sanitize_value(target, 0)
            new_stop = sanitize_value(stop, 0)

            is_buy = "BUY" in (rating or "BUY").upper()

            if new_target == 0 and new_entry > 0:
                new_target = new_entry * (1.10 if is_buy else 0.90)
            if new_stop == 0 and new_entry > 0:
                new_stop = new_entry * (0.96 if is_buy else 1.04)

            if new_entry != entry or new_target != target or new_stop != stop:
                conn.execute(text("""
                    UPDATE live_signals
                    SET entry_price = :e, target_price = :t, stop_loss_price = :s
                    WHERE id = :id
                """), {"e": new_entry, "t": new_target, "s": new_stop, "id": sid})
                updated_count += 1

        print(f"[+] Sanitized {updated_count} signals in live_signals table.")

        # 2. Scour Stocks Table for JSON NaN/Inf
        print("[*] Cleaning JSON columns in stocks table...")
        stocks = conn.execute(text("SELECT symbol, structured_consensus, analysis FROM stocks")).fetchall()

        def clean_json_str(js_str):
            if not js_str: return None
            try:
                data = json.loads(js_str)
                def _recursive_clean(obj):
                    if isinstance(obj, dict):
                        return {k: _recursive_clean(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [_recursive_clean(i) for i in obj]
                    elif isinstance(obj, float):
                        if math.isnan(obj) or math.isinf(obj): return None
                    return obj
                return json.dumps(_recursive_clean(data))
            except:
                return js_str

        for s in stocks:
            sym, sc, ana = s
            new_sc = clean_json_str(sc)
            new_ana = clean_json_str(ana)

            if new_sc != sc or new_ana != ana:
                conn.execute(text("""
                    UPDATE stocks
                    SET structured_consensus = :sc, analysis = :ana
                    WHERE symbol = :sym
                """), {"sc": new_sc, "ana": new_ana, "sym": sym})

        print("[+] Stock JSON columns scrubbed.")

    print("--- SANITIZATION COMPLETE ---")

if __name__ == "__main__":
    run_sanitization()
