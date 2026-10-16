"""
================================================================================
TradeMindAI: Authoritative Signal Ledger Exporter (v2.3-PROD)
================================================================================
Exports genuine persisted signal records from the authoritative database ledger
(ShadowSignalDB) to web/public/signals_history.json.
Fails visibly if the database is unavailable. Never manufactures synthetic data.
"""

import os
import json
import datetime
from backend.core.postgres import SessionLocal, ShadowSignalDB, engine
from backend.api.v1.endpoints.equity import is_eligible_buy
from backend.app.main import ensure_sqlite_columns

def export_history():
    print("[Export History] Ensuring SQLite schema columns...")
    ensure_sqlite_columns(eng=engine)
    print("[Export History] Connecting to authoritative database ledger...")
    try:
        with SessionLocal() as session:
            all_records = session.query(ShadowSignalDB).all()
            eligible = [r for r in all_records if is_eligible_buy(r)]

            records = []
            target_hits = 0
            stop_losses = 0
            expired = 0

            for s in eligible:
                data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
                for k, v in data.items():
                    if isinstance(v, datetime.datetime):
                        data[k] = v.isoformat()

                status = str(data.get("status", "")).upper()
                if status == "TARGET_HIT":
                    target_hits += 1
                elif status == "STOP_LOSS":
                    stop_losses += 1
                elif status == "EXPIRED":
                    expired += 1

                records.append(data)

            payload = {
                "records": records,
                "total": len(records),
                "summary": {
                    "total": len(records),
                    "target_hits": target_hits,
                    "stop_losses": stop_losses,
                    "expired": expired
                },
                "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source": "AUTHORITATIVE_PERSISTED_LEDGER"
            }

            os.makedirs('web/public', exist_ok=True)
            json_path = os.path.abspath('web/public/signals_history.json')
            with open(json_path, 'w') as f:
                json.dump(payload, f, indent=2)

            print(f"Successfully exported {len(records)} authentic persisted records to {json_path}")

    except Exception as e:
        print(f"[!] CRITICAL: Failed to export authoritative history: {e}")
        raise RuntimeError(f"Database history export failed: {e}") from e

if __name__ == "__main__":
    export_history()
