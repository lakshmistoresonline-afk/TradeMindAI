import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, ShadowSignalDB, PriceDB
from backend.domain.models.ios import LiveSignal
from backend.services.signal_engine import SignalEngine
from backend.core.container import container
from sqlalchemy import text

class SignalReplayEngine:
    """
    Deterministic Signal Replay Mechanism (Phase 14).
    Validates V2.3 Shadow Gate against historical candidates.
    """

    @staticmethod
    async def replay_shadow_gate(limit: int = 50) -> Dict[str, Any]:
        """
        Reruns V2.3 shadow gate on historical V2.2 signals using stored evidence.
        """
        results = []

        with SessionLocal() as db:
            # 1. Fetch historical signals that have provenance
            signals = db.query(ShadowSignalDB).filter(
                ShadowSignalDB.strategy_version == "v2.2"
            ).order_by(ShadowSignalDB.timestamp.desc()).limit(limit).all()

            from backend.services.signal_quality_gate import SignalQualityGate

            for s in signals:
                # 2. Reconstruct historical features (Mocking for now as full reconstruction requires DuckDB-TA sync)
                # Truth Rule: Use stored probabilities and levels as baseline
                mock_signal = container.ios_repo._map_db_to_live_signal(s)

                # features are needed for RSI experimental gate
                # Try to fetch last known features if available or mock
                features = {"rsi_14": 50.0} # Baseline neutral

                gate_res = SignalQualityGate.evaluate_v23_gate(mock_signal, features)

                results.append({
                    "signal_id": s.id,
                    "symbol": s.symbol,
                    "original_status": s.status,
                    "v23_decision": gate_res["decision"],
                    "v23_reasons": gate_res["reasons"]
                })

        # Aggregate stats
        total = len(results)
        blocked = len([r for r in results if r["v23_decision"] == "BLOCK"])

        # Calculate prevented losses (historical hindsight)
        losses_prevented = len([r for r in results if r["v23_decision"] == "BLOCK" and r["original_status"] == "STOP_LOSS"])
        winners_lost = len([r for r in results if r["v23_decision"] == "BLOCK" and r["original_status"] == "TARGET_HIT"])

        return {
            "replay_version": "v2.3.0_RECON",
            "total_processed": total,
            "blocked": blocked,
            "losses_prevented": losses_prevented,
            "winners_lost": winners_lost,
            "net_gate_efficiency": losses_prevented - winners_lost,
            "details": results
        }
