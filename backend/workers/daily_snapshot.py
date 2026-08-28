import asyncio
import os
import sys
import datetime
import json
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB, ShadowScanDiagnosticDB
from backend.services.portfolio_engine import ShadowPortfolioEngine

async def run_daily_snapshot():
    """
    Worker to record EOD equity, drawdown, and signal state distribution.
    Implements Phase AC and Section 42.
    Fully populates daily_metrics table.
    """
    print(f"[*] Starting Daily Snapshot [{datetime.datetime.now()}]")

    # 1. Calculate current shadow state
    state = ShadowPortfolioEngine.calculate_shadow_state()

    # 2. Collect Daily Metrics
    with SessionLocal() as session:
        today = datetime.date.today()

        # Outcome distribution today
        res = session.execute(text("""
            SELECT status, count(*)
            FROM shadow_signals
            WHERE outcome_timestamp::date = :today
            GROUP BY status
        """), {"today": today}).fetchall()
        counts = {r[0]: r[1] for r in res}

        # Signals generated today
        gen_today = session.query(ShadowSignalDB).filter(
            func.date(ShadowSignalDB.timestamp) == today
        ).count()

        # Provider Reliability (Section 43)
        total_evals = session.query(ShadowScanDiagnosticDB).filter(
            func.date(ShadowScanDiagnosticDB.scan_timestamp) == today
        ).count()

        failed_evals = session.query(ShadowScanDiagnosticDB).filter(
            func.date(ShadowScanDiagnosticDB.scan_timestamp) == today,
            ShadowScanDiagnosticDB.signal_decision == 'ERROR'
        ).count()

        avg_lat = session.query(func.avg(ShadowScanDiagnosticDB.provider_latency_ms)).filter(
            func.date(ShadowScanDiagnosticDB.scan_timestamp) == today
        ).scalar() or 0

        # 3. Persist to daily_metrics
        try:
            session.execute(text("""
                INSERT INTO daily_metrics (
                    date, universe_version,
                    signals_generated, signals_active,
                    target_hits, stop_losses, timeouts, expired, cancelled,
                    gross_pnl, net_pnl, virtual_equity, drawdown, exposure,
                    provider_reliability_pct, avg_latency_ms
                ) VALUES (
                    :date, :univ,
                    :gen, :active,
                    :targets, :stops, :timeouts, :expired, :cancelled,
                    :gross, :net, :equity, :dd, :exposure,
                    :rel, :lat
                ) ON CONFLICT (date) DO UPDATE SET
                    signals_active = EXCLUDED.signals_active,
                    target_hits = EXCLUDED.target_hits,
                    stop_losses = EXCLUDED.stop_losses,
                    net_pnl = EXCLUDED.net_pnl,
                    virtual_equity = EXCLUDED.virtual_equity,
                    drawdown = EXCLUDED.drawdown,
                    exposure = EXCLUDED.exposure,
                    provider_reliability_pct = EXCLUDED.provider_reliability_pct,
                    last_updated = CURRENT_TIMESTAMP
            """), {
                "date": today,
                "univ": "NIFTY_200_AUG2026",
                "gen": gen_today,
                "active": state["active_count"],
                "targets": counts.get("TARGET_HIT", 0),
                "stops": counts.get("STOP_LOSS", 0),
                "timeouts": counts.get("TIMEOUT", 0),
                "expired": counts.get("EXPIRED", 0),
                "cancelled": counts.get("CANCELLED", 0),
                "gross": state["realized_pnl"] + 0.20 * (counts.get("TARGET_HIT", 0) + counts.get("STOP_LOSS", 0)), # Heuristic
                "net": state["realized_pnl"],
                "equity": state["current_equity"],
                "dd": state["drawdown"],
                "exposure": state["gross_exposure"],
                "rel": round((1 - (failed_evals / total_evals if total_evals > 0 else 0)) * 100, 2),
                "lat": int(avg_lat)
            })
            session.commit()
            print(f"[SUCCESS] Daily Snapshot Recorded for {today}. Equity={state['current_equity']}")
        except Exception as e:
            print(f"[!] Error recording daily metric: {e}")
            session.rollback()

if __name__ == "__main__":
    from sqlalchemy import func
    asyncio.run(run_daily_snapshot())
