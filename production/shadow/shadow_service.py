
import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from typing import Optional, Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from backend.core.container import container
from backend.core.postgres import ShadowSignalDB, engine
from backend.services.outcome_engine import OutcomeEngine

class ShadowService:
    STRATEGY_VERSION = "v2.2"
    DRAWDOWN_LIMIT = 15.0

    @staticmethod
    async def run_shadow_cycle():
        """
        Executes a full shadow trading cycle:
        1. Check current drawdown.
        2. Scan universe for signals.
        3. Persist new shadow signals.
        4. Audit existing signals for outcomes.
        """
        print(f"[*] Starting Shadow Cycle [{datetime.utcnow()}]")

        # 1. Check Drawdown
        current_dd = ShadowService.calculate_current_drawdown()
        if current_dd > ShadowService.DRAWDOWN_LIMIT:
            print(f"[!] CRITICAL: Drawdown limit exceeded ({current_dd:.2f}%). Shadow trading halted.")
            return

        # 2. Scan Universe
        from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
        for symbol in NIFTY_200_CONSTITUENTS:
            try:
                signal = await container.signal_engine.generate_signal(symbol, "EQUITY", "SWING")
                if signal:
                    ShadowService.persist_shadow_signal(signal)
            except Exception as e:
                print(f"Error generating signal for {symbol}: {e}")

        # 3. Resolve Outcomes
        await ShadowService.audit_open_signals()

    @staticmethod
    def calculate_current_drawdown() -> float:
        with container.repository.session_factory() as session:
            query = text("SELECT net_return FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED')")
            res = session.execute(query).fetchall()
            if not res: return 0.0

            returns = [r[0] for r in res if r[0] is not None]
            if not returns: return 0.0

            cum_returns = (1 + pd.Series(returns)/100).cumprod()
            peak = cum_returns.expanding().max()
            dd = (cum_returns / peak - 1) * 100
            return abs(float(dd.min()))

    @staticmethod
    def persist_shadow_signal(signal):
        with container.repository.session_factory() as session:
            # Check for existing active signal for same symbol
            existing = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.symbol == signal.symbol,
                ShadowSignalDB.status == 'ACTIVE'
            ).first()
            if existing: return

            db_sig = ShadowSignalDB(
                id=signal.id,
                timestamp=signal.timestamp,
                symbol=signal.symbol,
                direction=signal.direction,
                raw_probability=signal.raw_probability,
                calibrated_probability=signal.calibrated_probability,
                expected_value=signal.expected_value,
                data_quality_score=signal.data_quality_score,
                entry_price=signal.entry_price,
                target_price=signal.target_price,
                stop_price=signal.stop_loss_price,
                strategy_version=ShadowService.STRATEGY_VERSION,
                model_version=signal.model_version,
                feature_version=signal.provenance.get("feature_version", "v1.0.0"),
                regime=signal.regime,
                status="ACTIVE",
                provenance_json=str(signal.provenance)
            )
            session.add(db_sig)
            session.commit()
            print(f"   [SHADOW] Signal Logged: {signal.symbol} {signal.direction} @ {signal.entry_price}")

    @staticmethod
    async def audit_open_signals():
        with container.repository.session_factory() as session:
            active_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()

            for sig in active_signals:
                # Fetch recent prices
                prices = await container.repository.get_recent_prices(sig.symbol, limit=50)
                if not prices: continue

                df = pd.DataFrame([p.model_dump() for p in prices])
                df.set_index('date', inplace=True)
                df.sort_index(inplace=True)
                df.columns = [c.capitalize() for c in df.columns]

                # Reconstruct signal for OutcomeEngine
                from backend.domain.models.ios import LiveSignal
                sig_obj = LiveSignal(
                    id=sig.id, symbol=sig.symbol, timestamp=sig.timestamp,
                    entry_price=sig.entry_price, target_price=sig.target_price, stop_loss_price=sig.stop_price,
                    direction=sig.direction, status="ACTIVE", conviction=sig.calibrated_probability*100,
                    rating="BUY", timeframe="SWING"
                )

                outcome = OutcomeEngine.evaluate_outcome(sig_obj, df[df.index > sig.timestamp])

                if outcome["status"] in ["TARGET_HIT", "STOP_LOSS", "EXPIRED"]:
                    sig.status = outcome["status"]
                    sig.outcome_timestamp = outcome["outcome_date"]
                    sig.realized_return = outcome["profit_pct"]
                    sig.realized_mfe = outcome["mfe"]
                    sig.realized_mae = outcome["mae"]

                    # Apply friction to net_return
                    friction = 0.20 # round trip
                    sig.transaction_cost = 0.10
                    sig.slippage = 0.10
                    sig.net_return = outcome["profit_pct"] - friction

                    print(f"   [SHADOW] Signal Resolved: {sig.symbol} -> {sig.status} ({sig.net_return:.2f}%)")

            session.commit()

if __name__ == "__main__":
    asyncio.run(ShadowService.run_shadow_cycle())
