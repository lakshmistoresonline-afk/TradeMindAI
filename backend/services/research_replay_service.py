import datetime
import uuid
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB
from backend.services.signal_engine import SignalEngine
from backend.services.outcome_service import OutcomeService
from backend.core.container import container

class ResearchReplayService:
    """
    Phases 13-16: Replay Execution Accounting and Reconciliation.
    Enforces no silent skips and three-way classification.
    """

    @staticmethod
    async def run_full_replay(
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        strategy_version: str = "v2.2"
    ) -> Dict[str, Any]:
        from backend.domain.models.data_platform import ResearchRun
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        symbols = container.universe_service.NIFTY_200_CONSTITUENTS

        run_obj = ResearchRun(
            id=run_id,
            strategy_version=strategy_version,
            start_timestamp=datetime.datetime.utcnow(),
            status="RUNNING"
        )

        accounting = []
        total_signals = 0
        eligible_count = 0

        for symbol in symbols:
            record = {
                "research_run_id": run_id,
                "symbol": symbol,
                "status": "PENDING",
                "bars_evaluated": 0,
                "signals_generated": 0,
                "failure_reason": None,
                "eligible": False,
                "model_available": False
            }

            try:
                # 1. Eligibility Check
                stock = await container.repository.get_stock_by_symbol(symbol)
                if not stock:
                    record["status"] = "REPLAY_INCOMPLETE"
                    record["failure_reason"] = "NO_HISTORICAL_DATA"
                    accounting.append(record)
                    continue

                record["eligible"] = True
                eligible_count += 1

                # Check model
                champion = await container.model_registry.get_champion(symbol)
                if champion:
                    record["model_available"] = True

                # 2. Fetch Data
                df = await container.provider.get_history(symbol, start_date=start_date, end_date=end_date)
                if df.empty:
                    record["status"] = "REPLAY_INCOMPLETE"
                    record["failure_reason"] = "DATA_UNAVAILABLE"
                    accounting.append(record)
                    continue

                record["bars_available"] = len(df)

                # 3. Iterate through bars (Replay)
                for ts, row in df.iterrows():
                    record["bars_evaluated"] += 1

                    # Call Signal Engine for this point in time
                    # SignalEngine.generate_signal needs to be time-aware
                    signal = await SignalEngine.generate_signal(
                        symbol=symbol,
                        asset_class="EQUITY",
                        timeframe="SWING",
                        evaluation_timestamp=ts.to_pydatetime()
                    )

                    if signal:
                        record["signals_generated"] += 1
                        # Persist to ShadowSignalDB for research
                        await ResearchReplayService._persist_research_signal(signal, run_id)

                record["status"] = "COMPLETED"
                total_signals += record["signals_generated"]

            except Exception as e:
                record["status"] = "REPLAY_ENGINE_DEFECT"
                record["failure_reason"] = f"EXCEPTION: {str(e)}"

            accounting.append(record)

        run_obj.end_timestamp = datetime.datetime.utcnow()
        run_obj.status = "COMPLETED"
        run_obj.eligible_count = eligible_count
        run_obj.signal_count = total_signals
        run_obj.replay_completed = len(symbols)

        return {
            "run": run_obj.model_dump(),
            "total_symbols": len(symbols),
            "signals_generated": total_signals,
            "accounting": accounting
        }

    @staticmethod
    async def _persist_research_signal(signal: Any, run_id: str):
        with SessionLocal() as db:
            signal_data = signal.model_dump()
            signal_data["run_id"] = run_id
            signal_data["dataset_type"] = "V2.2_HISTORICAL_REPLAY"

            # Map to ShadowSignalDB
            db_obj = ShadowSignalDB(**{k: v for k, v in signal_data.items() if hasattr(ShadowSignalDB, k)})
            db.add(db_obj)
            db.commit()
