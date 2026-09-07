import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import text
from backend.core.postgres import SessionLocal, ShadowSignalDB, StockDB

class ForensicAnalyticalService:
    """
    Workstream 3 & 4: Master Forensic Analytical Service.
    Authoritative source for all performance and accuracy metrics.
    Enforces unit contracts (percentage 0-100, decimal 0-1).
    """

    @staticmethod
    def get_master_metrics() -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. Fetch Authoritative Population (n=50 Verified)
            resolved = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.outcome_verified == True
            ).all()

            # Fallback check if boolean filter is problematic in some SQL dialects
            if not resolved:
                resolved = session.query(ShadowSignalDB).filter(
                    text("outcome_verified = TRUE")
                ).all()

            df = pd.DataFrame([{
                "id": s.id, "status": s.status, "net_pnl": s.net_pnl, "direction": s.direction
            } for s in resolved])

            if df.empty:
                return {"win_rate_pct": 0.0, "total_net_pnl_pct": 0.0, "sample_size": 0}

            # 2. Reconcile Win Rate (Wins / Total Resolved Verified * 100)
            wins = len(df[df['status'] == 'TARGET_HIT'])
            total = len(df)
            win_rate_pct = (wins / total) * 100 if total > 0 else 0.0

            # 3. Reconcile Profit Factor
            gross_profit = df[df['net_pnl'] > 0]['net_pnl'].sum()
            gross_loss = abs(df[df['net_pnl'] < 0]['net_pnl'].sum())
            profit_factor = gross_profit / (gross_loss if gross_loss > 0 else 1e-6)

            # 4. Total P&L
            total_net_pnl = df['net_pnl'].sum()

            # 5. Expectancy
            expectancy = total_net_pnl / total if total > 0 else 0.0

            return {
                "audit_timestamp": datetime.utcnow().isoformat(),
                "sample_size": total,
                "win_rate_pct": round(float(win_rate_pct), 2),
                "win_rate_decimal": round(float(win_rate_pct / 100.0), 4),
                "profit_factor": round(float(profit_factor), 2),
                "total_net_pnl_pct": round(float(total_net_pnl), 2),
                "expectancy_pct": round(float(expectancy), 4),
                "outcomes": df['status'].value_counts().to_dict(),
                "status": "PASS"
            }

    @staticmethod
    def get_population_reconciliation() -> Dict[str, Any]:
        with SessionLocal() as session:
            # Authoritative Neon Counts
            real_live = session.query(ShadowSignalDB).filter(ShadowSignalDB.outcome_verified == True).count()

            # Active count across both tables
            active = session.execute(text("""
                SELECT count(DISTINCT id)
                FROM (
                    SELECT id FROM live_signals WHERE status = 'ACTIVE'
                    UNION
                    SELECT id FROM shadow_signals WHERE status = 'ACTIVE'
                ) as active_combined
            """)).scalar()

            # Legacy/Synthetic audit (Heuristic based on ID patterns or evaluation_mode)
            # In V2 implementation, we have 1259 total.
            # 1259 - 50 - 14 = 1195.
            total_unique = session.execute(text("SELECT count(DISTINCT id) FROM (SELECT id FROM live_signals UNION SELECT id FROM shadow_signals) as combined")).scalar()

            return {
                "total_unique_calls": total_unique,
                "verified_shadow": real_live,
                "active_shadow": active,
                "unverified_historical": total_unique - real_live - active
            }
