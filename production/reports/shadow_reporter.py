
import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from backend.core.postgres import SessionLocal, ShadowSignalDB

class ShadowReporter:
    @staticmethod
    def generate_outcome_reports(signal_id: str):
        """
        Generates individual and cumulative outcome reports from the database.
        """
        print(f"[*] Generating Outcome Reports for {signal_id}...")

        with SessionLocal() as session:
            sig = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
            if not sig:
                print(f"[!] Error: Signal {signal_id} not found in DB.")
                return

            if sig.status == 'ACTIVE':
                print(f"[!] Warning: Signal {signal_id} is still ACTIVE. Skipping report.")
                return

            # 1. Calculate Completed Count
            completed_count = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.status.in_(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'TIMEOUT', 'AMBIGUOUS', 'INVALID'])
            ).count()

            # 2. Map Status to Friendly Outcome
            status_map = {
                "TARGET_HIT": "WIN",
                "STOP_LOSS": "LOSS",
                "EXPIRED": "TIMEOUT",
                "TIMEOUT": "TIMEOUT",
                "AMBIGUOUS": "AMBIGUOUS",
                "INVALID": "INVALID"
            }
            outcome_label = status_map.get(sig.status, sig.status)

            # 3. Create Detailed Report
            report_content = f"""# Shadow Outcome Report - {sig.symbol}

## Signal Identification
- **SIGNAL ID:** {sig.id}
- **SYMBOL:** {sig.symbol}
- **STRATEGY VERSION:** {sig.strategy_version}
- **MODEL VERSION:** {sig.model_version}

## Trade Parameters
- **SIGNAL TIMESTAMP:** {sig.timestamp}
- **DIRECTION:** {sig.direction}
- **ENTRY PRICE:** {sig.entry_price:.2f}
- **TARGET:** {sig.target_price:.2f}
- **STOP:** {sig.stop_price:.2f}

## Execution & Outcome
- **OUTCOME:** {outcome_label}
- **EXIT PRICE:** {sig.entry_price * (1 + sig.realized_return/100) if sig.realized_return else 0.0:.2f}
- **EXIT TIMESTAMP:** {sig.outcome_timestamp}
- **HOLDING PERIOD:** {str(sig.outcome_timestamp - (sig.timestamp if isinstance(sig.timestamp, datetime) else datetime.fromisoformat(sig.timestamp))) if sig.outcome_timestamp else "N/A"}

## Performance Metrics
- **GROSS RETURN:** {sig.realized_return:.2f}%
- **TRANSACTION COST:** {sig.transaction_cost:.2f}%
- **SLIPPAGE:** {sig.slippage:.2f}%
- **NET RETURN:** {sig.net_return:.2f}%
- **MFE:** {sig.realized_mfe:.2f}%
- **MAE:** {sig.realized_mae:.2f}%

## Progress
- **COMPLETED TRADES / 20:** {completed_count} / 20

---
> [!NOTE]
> This is an automated shadow trading audit. No real capital was deployed.
"""
            report_path = f"production/reports/SHADOW_OUTCOME_{sig.id}.md"
            os.makedirs("production/reports", exist_ok=True)
            with open(report_path, "w") as f:
                f.write(report_content)

            # 4. Update Latest Outcome
            latest_path = "production/reports/SHADOW_LATEST_OUTCOME.md"
            with open(latest_path, "w") as f:
                f.write(report_content)

            print(f"[SUCCESS] Reports generated: {report_path} and {latest_path}")

    @staticmethod
    def get_latest_outcome_summary():
        with SessionLocal() as session:
            latest = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.status.in_(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])
            ).order_by(ShadowSignalDB.outcome_timestamp.desc()).first()

            if not latest: return "N/A"
            return f"{latest.symbol} {latest.status} ({latest.net_return:.2f}%) at {latest.outcome_timestamp}"
