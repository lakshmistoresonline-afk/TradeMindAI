import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def validate():
    db_url = os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not set.")
        sys.exit(1)

    engine = create_engine(db_url)
    print("============================================================")
    print(" NIFTY 200 STEP 2 — SIGNAL INTEGRITY AUDIT")
    print("============================================================")

    try:
        with engine.connect() as conn:
            # 1. Fetch Master & Active Signals
            res = conn.execute(text("SELECT * FROM live_signals WHERE id LIKE 'master_%' OR status = 'ACTIVE'"))
            signals = res.fetchall()
            cols = res.keys()

            print(f"[*] Auditing {len(signals)} baseline signals...")

            audit_failures = []

            # Table Header
            print(f"{'SYMBOL':<12} | {'DIR':<5} | {'ENTRY':<8} | {'TGT':<8} | {'SL':<8} | {'PROB':<5} | {'EV':<6} | {'RR':<5} | {'STATUS':<10}")
            print("-" * 90)

            for s_row in signals:
                s = dict(zip(cols, s_row))

                symbol = s['symbol']
                direction = s['direction']
                entry = s['entry_price']
                target = s['target_price']
                stop = s['stop_loss_price']
                prob = s['calibrated_probability']
                ev = s['expected_value']
                rr = s['risk_reward']
                status = s['status']

                # Integrity Checks
                errors = []
                if direction == "LONG":
                    if not (target > entry > stop): errors.append("Invalid LONG levels (TGT > Entry > SL failed)")
                elif direction == "SHORT":
                    if not (target < entry < stop): errors.append("Invalid SHORT levels (TGT < Entry < SL failed)")

                if prob is None or not (0 <= prob <= 1): errors.append(f"Invalid Probability: {prob}")
                if ev is None: errors.append("EV is NULL")
                if rr is None or rr <= 0: errors.append(f"Invalid R:R: {rr}")

                # Metadata check (Part 2 & 19)
                prov = json.loads(s['provenance']) if s['provenance'] else {}
                if not prov.get('universe_version') or not prov.get('data_timestamp'):
                    errors.append("Missing Provenance (Universe Ver / Data TS)")

                if errors:
                    audit_failures.append(f"{symbol}: {', '.join(errors)}")

                prob_str = f"{prob:5.2f}" if prob is not None else "MISS "
                ev_str = f"{ev:6.1f}" if ev is not None else "MISS "
                rr_str = f"{rr:5.2f}" if rr is not None else "MISS "

                print(f"{symbol:<12} | {direction:<5} | {entry:<8.1f} | {target:<8.1f} | {stop:<8.1f} | {prob_str} | {ev_str} | {rr_str} | {status:<10}")

            print("-" * 90)

            # 2. F&O Coverage Semantics (Part 3)
            res = conn.execute(text("SELECT count(*) FROM instruments WHERE segment IN ('FUTURES', 'OPTIONS')"))
            fo_count = res.scalar()
            fo_status = "PARTIAL" if fo_count < 100 else "FULL" # Heuristic
            print(f"\n[*] F&O Coverage Status: {fo_status} ({fo_count} contracts seeded)")

            # 3. Final Conclusion
            if audit_failures:
                print("\n[!] AUDIT FAILURES DETECTED:")
                for f in audit_failures: print(f"    - {f}")
                print("\nSTATUS: NIFTY200_STEP2_SIGNAL_INTEGRITY_FAILURE")
                sys.exit(1)
            else:
                print("\n[SUCCESS] All baseline signals passed P0 integrity gates.")
                print("STATUS: NIFTY200_STEP2_SIGNAL_INTEGRITY_PASS")
                sys.exit(0)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate()
