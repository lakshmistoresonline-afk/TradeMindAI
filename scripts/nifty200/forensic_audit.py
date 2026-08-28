import os
import sys
import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import SessionLocal, LiveSignalDB, StockDB

async def run_audit():
    print("============================================================")
    print(" NIFTY 200 STEP 2A — FORENSIC AUDIT ENGINE")
    print("============================================================")

    db = SessionLocal()
    provider = container.provider

    # --- PART 1 & 2 & 3 & 11 & 12: COMPLETE 11-SIGNAL AUDIT ---
    print("\n[*] Auditing Signal Identity & Quantitative Integrity...")
    signals = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    audit_data = []
    for sig in signals:
        # Re-fetch current price independently (Part 4)
        current_market_price = await provider.get_ltp(sig.symbol)

        # Provenance Check (Part 2 & 10)
        prov = json.loads(sig.provenance) if sig.provenance else {}

        # Calculate Distances (Part 3)
        target_pct = ((sig.target_price - sig.entry_price) / sig.entry_price) * 100
        stop_pct = ((sig.entry_price - sig.stop_loss_price) / sig.entry_price) * 100

        # Look-ahead verification (Part 10)
        data_ts_str = prov.get('data_timestamp')
        created_at = sig.timestamp
        lookahead_fail = False
        if data_ts_str:
            data_ts = datetime.fromisoformat(data_ts_str)
            if data_ts > created_at: lookahead_fail = True

        audit_data.append({
            "SIGNAL_ID": sig.id,
            "SYMBOL": sig.symbol,
            "TYPE": sig.asset_class,
            "DIR": sig.direction,
            "CREATED": sig.timestamp.strftime("%H:%M:%S"),
            "ENTRY": sig.entry_price,
            "TARGET": sig.target_price,
            "STOP": sig.stop_loss_price,
            "CURRENT": current_market_price,
            "PROB": sig.calibrated_probability,
            "EV": sig.expected_value,
            "RR": sig.risk_reward,
            "STATUS": sig.status,
            "TGT_%": round(target_pct, 2),
            "SL_%": round(stop_pct, 2),
            "LOOKAHEAD": "FAIL" if lookahead_fail else "PASS"
        })

    df_signals = pd.DataFrame(audit_data)
    print(df_signals.to_string(index=False))

    # --- PART 5 & 6: MARKET DATA FORENSICS (ALL 200) ---
    print("\n[*] Phase 5: Market Data Forensics (Complete Universe)...")
    stocks = db.query(StockDB).filter(StockDB.index_membership == 'NIFTY_200').all()

    ages = []
    stale_count = 0
    missing_count = 0
    now = datetime.now()

    for s in stocks:
        if s.updated_at:
            age = (now - s.updated_at).total_seconds()
            ages.append(age)
            if age > 3600: stale_count += 1
        else:
            missing_count += 1

    if ages:
        print(f"   Universe Records: {len(stocks)}")
        print(f"   Average Data Age: {np.mean(ages):.1f}s")
        print(f"   Median Data Age:  {np.median(ages):.1f}s")
        print(f"   P95 Data Age:     {np.percentile(ages, 95):.1f}s")
        print(f"   Stale (>1h):      {stale_count}")
        print(f"   Missing Sync:     {missing_count}")

    # --- PART 14: F&O COVERAGE ---
    from backend.core.postgres import InstrumentDB
    fo_contracts = db.query(InstrumentDB).all()
    print(f"\n[*] F&O Coverage Audit ({len(fo_contracts)} Baseline Contracts):")
    for c in fo_contracts:
        print(f"   - {c.id:<20} | {c.underlying_symbol:<10} | {c.segment:<8} | Expiry: {c.expiry}")

    # --- PART 17 & 18: API & FIRESTORE RECONCILIATION ---
    print("\n[*] Phase 17: Cross-Tier Reconciliation Sample (Neon vs Domain)...")
    from backend.domain.models.ios import LiveSignal
    try:
        db_sig = signals[0]
        domain_sig = container.ios_repo._map_db_to_live_signal(db_sig)

        reconciled = (
            db_sig.entry_price == domain_sig.entry_price and
            db_sig.calibrated_probability == domain_sig.calibrated_probability and
            db_sig.expected_value == domain_sig.expected_value
        )
        print(f"   Neon -> Domain Model: {'MATCH' if reconciled else 'MISMATCH'}")
    except Exception as e:
        print(f"   [ERROR] Reconciliation failed: {e}")

    db.close()
    print("\n============================================================")
    print(" FORENSIC AUDIT COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(run_audit())
