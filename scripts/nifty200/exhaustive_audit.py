import os
import sys
import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import SessionLocal, LiveSignalDB, StockDB

async def run_audit():
    db = SessionLocal()
    provider = container.provider
    now = datetime.now()

    # 1. RETRIEVE ALL 11 SIGNALS
    sigs = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    audit_results = []
    for i, sig in enumerate(sigs, 1):
        # Independently fetch current price (Part 4)
        try:
            curr_price = await provider.get_ltp(sig.symbol)
        except:
            curr_price = 0.0

        prov = json.loads(sig.provenance) if sig.provenance else {}
        data_ts_str = prov.get('data_timestamp')

        # Look-ahead check (Part 10)
        lookahead = "PASS"
        if data_ts_str:
            data_ts = datetime.fromisoformat(data_ts_str)
            if data_ts > sig.timestamp:
                lookahead = "FAIL"

        # Distances & RR (Part 3 & 14)
        reward = abs(sig.target_price - sig.entry_price)
        risk = abs(sig.entry_price - sig.stop_loss_price)
        rr = round(reward/risk, 2) if risk > 0 else 0
        tgt_pct = round((reward / sig.entry_price) * 100, 2)
        sl_pct = round((risk / sig.entry_price) * 100, 2)

        audit_results.append({
            "#": i,
            "SIGNAL_ID": sig.id,
            "SYMBOL": sig.symbol,
            "TYPE": sig.asset_class,
            "DIR": sig.direction,
            "CREATED": sig.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "MARKET_TS": data_ts_str.split('T')[1] if data_ts_str else "N/A",
            "ENTRY": sig.entry_price,
            "TARGET": sig.target_price,
            "STOP": sig.stop_loss_price,
            "CURRENT": curr_price,
            "PROB": sig.calibrated_probability,
            "EV": sig.expected_value,
            "R:R": rr,
            "STATUS": sig.status,
            "LOOKAHEAD": lookahead,
            "STRAT": prov.get('strategy_version', 'v2.2'),
            "UNIV": prov.get('universe_version', 'v1.0.0')
        })

    # 2. MARKET DATA FORENSICS (200 Constituents)
    stocks = db.query(StockDB).filter(StockDB.index_membership == 'NIFTY_200').all()
    ages = [(now - s.updated_at).total_seconds() for s in stocks if s.updated_at]

    universe_stats = {
        "count": len(stocks),
        "min": np.min(ages) if ages else 0,
        "max": np.max(ages) if ages else 0,
        "avg": np.mean(ages) if ages else 0,
        "med": np.median(ages) if ages else 0,
        "p95": np.percentile(ages, 95) if ages else 0,
        "stale": len([a for a in ages if a > 3600]),
        "missing": len(stocks) - len(ages)
    }

    # Output
    print("---SIGNAL_TABLE---")
    df = pd.DataFrame(audit_results)
    print(df.to_string(index=False))

    print("\n---UNIVERSE_STATS---")
    print(json.dumps(universe_stats, indent=2))

    db.close()

if __name__ == "__main__":
    asyncio.run(run_audit())
