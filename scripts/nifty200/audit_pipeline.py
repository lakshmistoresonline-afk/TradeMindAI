import os
import sys
import asyncio
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import SessionLocal, LiveSignalDB, StockDB

async def audit():
    print("============================================================")
    print(" NIFTY 200 STEP 2 — PIPELINE & DATA INTEGRITY AUDIT")
    print("============================================================")

    db = SessionLocal()
    provider = container.provider

    # 1. Market Data Refreshness (Part 4 & 5)
    print("\n[*] Phase 1: Market Data Completeness (NIFTY 200 Sample)...")
    stocks = db.query(StockDB).filter(StockDB.index_membership == 'NIFTY_200').limit(10).all()
    for s in stocks:
        status = "FRESH" if s.updated_at and (datetime.now() - s.updated_at).total_seconds() < 3600 else "STALE"
        price_str = f"{s.last_price:8.2f}" if s.last_price is not None else "MISSING "
        print(f"   - {s.symbol:<12} | Price: {price_str} | Updated: {s.updated_at} | Status: {status}")

    # 2. Intraday Data Availability (Part 22)
    print("\n[*] Phase 2: Intraday (1m) Data Availability...")
    try:
        df_1m = await provider.fetch_history('RELIANCE', period='1d', interval='1m')
        if not df_1m.empty:
            print(f"   [SUCCESS] RELIANCE 1m data: {len(df_1m)} bars retrieved.")
        else:
            print("   [!] WARNING: RELIANCE 1m data empty.")
    except Exception as e:
        print(f"   [ERROR] Intraday fetch failed: {e}")

    # 3. Signal Engine Validation (Part 8-16)
    print("\n[*] Phase 3: Signal Lifecycle & Risk Audit (11 Master Signals)...")
    signals = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    audit_table = []
    for sig in signals:
        # Part 11-13: Level Validation
        valid_levels = False
        if sig.direction == "LONG":
            valid_levels = (sig.target_price > sig.entry_price > sig.stop_loss_price)
        else:
            valid_levels = (sig.target_price < sig.entry_price < sig.stop_loss_price)

        # Part 15: Probability
        valid_prob = sig.calibrated_probability is not None and (0 <= sig.calibrated_probability <= 1)

        # Part 14: R:R
        reward = abs(sig.target_price - sig.entry_price)
        risk = abs(sig.entry_price - sig.stop_loss_price)
        rr = round(reward/risk, 2) if risk > 0 else 0

        audit_table.append({
            "SYMBOL": sig.symbol,
            "DIR": sig.direction,
            "LEVELS": "VALID" if valid_levels else "INVALID",
            "PROB": f"{sig.calibrated_probability:.2f}" if sig.calibrated_probability else "MISSING",
            "EV": f"{sig.expected_value:.1f}" if sig.expected_value else "MISSING",
            "R:R": rr,
            "STATUS": sig.status
        })

    df_audit = pd.DataFrame(audit_table)
    print(df_audit.to_string(index=False))

    # 4. API & Cross-Platform Verification (Part 27-30)
    print("\n[*] Phase 4: API Contract & Data Mapping Verification...")
    # This checks if the db_sig maps cleanly to the LiveSignal model (Pydantic)
    from backend.domain.models.ios import LiveSignal

    try:
        sample_sig = signals[0]
        # Pydantic conversion check
        domain_sig = container.ios_repo._map_db_to_live_signal(sample_sig)
        print(f"   [SUCCESS] Neon -> Domain Model Mapping verified for {domain_sig.symbol}")

        # Verify critical fields presence
        required = ['id', 'symbol', 'entry_price', 'target_price', 'stop_loss_price', 'calibrated_probability', 'expected_value', 'status']
        missing_fields = [f for f in required if getattr(domain_sig, f) is None]
        if not missing_fields:
            print("   [SUCCESS] API Contract fields verified.")
        else:
            print(f"   [!] WARNING: API Missing critical fields: {missing_fields}")
    except Exception as e:
        print(f"   [ERROR] Cross-platform reconciliation failed: {e}")

    db.close()
    print("\n============================================================")
    print(" AUDIT COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(audit())
