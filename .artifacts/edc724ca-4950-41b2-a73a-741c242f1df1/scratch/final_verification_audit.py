import os
import sys
import asyncio
import json
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append("D:/TradeMindAI")
load_dotenv("D:/TradeMindAI/backend/.env")

async def audit():
    from backend.core.postgres import engine

    results = {}

    try:
        with engine.connect() as conn:
            # 1. Sample Live BUY
            res = conn.execute(text("SELECT * FROM live_signals WHERE status = 'ACTIVE' AND rating LIKE '%BUY%' LIMIT 1"))
            results['live_buy'] = res.fetchone()

            # 2. Sample Live SELL
            res = conn.execute(text("SELECT * FROM live_signals WHERE status = 'ACTIVE' AND rating LIKE '%SELL%' LIMIT 1"))
            results['live_sell'] = res.fetchone()

            # 3. Sample Historical TARGET_HIT
            res = conn.execute(text("SELECT * FROM live_signals WHERE status = 'TARGET_HIT' LIMIT 1"))
            results['hist_hit'] = res.fetchone()

            # 4. Sample Historical STOP_LOSS
            res = conn.execute(text("SELECT * FROM live_signals WHERE status = 'STOP_LOSS' LIMIT 1"))
            results['hist_stop'] = res.fetchone()

            # 5. Sample Expired
            res = conn.execute(text("SELECT * FROM live_signals WHERE status = 'EXPIRED' LIMIT 1"))
            results['hist_expired'] = res.fetchone()

            # 6. Check for duplicate signals (same symbol, same timeframe)
            res = conn.execute(text("SELECT symbol, timeframe, count(*) FROM live_signals GROUP BY symbol, timeframe HAVING count(*) > 1 LIMIT 5"))
            results['duplicates'] = res.fetchall()

            # 7. Supporting data sample (Stock analysis)
            if results['live_buy']:
                symbol = results['live_buy'][1]
                res = conn.execute(text(f"SELECT symbol, analysis, structured_consensus, fii_holding FROM stocks WHERE symbol = '{symbol}'"))
                results['stock_data'] = res.fetchone()

            # Format rows as dicts for easier reading in report
            def row_to_dict(row, keys):
                if not row: return None
                return {k: str(v) if hasattr(v, 'isoformat') else v for k, v in zip(keys, row)}

            keys = ['id', 'symbol', 'timestamp', 'rating', 'direction', 'conviction', 'entry_price', 'target_price', 'stop_loss_price', 'timeframe', 'status', 'outcome_date', 'profit_pct', 'mfe', 'mae', 'model_version', 'validated_at', 'triggered_at', 'trigger_price', 'events', 'trigger_condition']

            final_report = {
                "live_buy": row_to_dict(results['live_buy'], keys),
                "live_sell": row_to_dict(results['live_sell'], keys),
                "hist_hit": row_to_dict(results['hist_hit'], keys),
                "hist_stop": row_to_dict(results['hist_stop'], keys),
                "hist_expired": row_to_dict(results['hist_expired'], keys),
                "duplicates": [list(r) for r in results['duplicates']],
                "stock_data_sample": row_to_dict(results['stock_data'], ['symbol', 'analysis', 'structured_consensus', 'fii_holding']) if 'stock_data' in results else None
            }

            print(json.dumps(final_report, indent=2))

    except Exception as e:
        import traceback
        print(f"DB Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(audit())
