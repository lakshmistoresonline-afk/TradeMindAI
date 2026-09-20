import datetime
from datetime import timezone
from typing import Dict, Any, Optional
import uuid
from backend.core.postgres import SessionLocal, SignalShadowDecisionDB
from backend.domain.models.ios import LiveSignal

class SignalShadowService:
    """
    V2.3 Shadow Decision Ledger Service.
    Records comparisons between V2.2 Production and V2.3 Shadow gates.
    """

    @staticmethod
    async def record_shadow_decision(
        v22_signal: Optional[LiveSignal],
        v23_gate_result: Dict[str, Any],
        candidate_data: Dict[str, Any]
    ):
        """
        Persists shadow decision record for future forensic validation.
        """
        with SessionLocal() as db:
            try:
                decision_id = str(uuid.uuid4())

                # Extract V2.2 Baseline
                v22_decision = "PUBLISH" if v22_signal else "NO_SIGNAL"
                v22_prob = v22_signal.calibrated_probability if v22_signal else candidate_data.get("calibrated_prob")
                v22_ev = v22_signal.expected_value if v22_signal else candidate_data.get("expected_val")

                # Extract V2.3 Candidate
                v23_decision = v23_gate_result.get("decision", "BLOCK")
                if v22_decision == "NO_SIGNAL":
                     v23_decision = "NO_SIGNAL"

                shadow_rec = SignalShadowDecisionDB(
                    id=decision_id,
                    signal_id=v22_signal.id if v22_signal else None,
                    candidate_id=candidate_data.get("candidate_id"),
                    current_engine="v2.2",
                    shadow_engine="v2.3",
                    current_decision=v22_decision,
                    shadow_decision=v23_decision,
                    current_probability=float(v22_prob) if v22_prob else 0.0,
                    shadow_probability=float(v22_prob) if v22_prob else 0.0,
                    current_ev=float(v22_ev) if v22_ev else 0.0,
                    shadow_ev=float(v22_ev) if v22_ev else 0.0,
                    current_entry=float(v22_signal.entry_price) if v22_signal else float(candidate_data.get("price") or 0),
                    shadow_entry=float(v22_signal.entry_price) if v22_signal else float(candidate_data.get("price") or 0),
                    current_stop=float(v22_signal.stop_price) if v22_signal and v22_signal.stop_price else None,
                    shadow_stop=float(v22_signal.stop_price) if v22_signal and v22_signal.stop_price else None,
                    current_target=float(v22_signal.target_price) if v22_signal and v22_signal.target_price else None,
                    shadow_target=float(v22_signal.target_price) if v22_signal and v22_signal.target_price else None,
                    current_regime=candidate_data.get("regime_label"),
                    shadow_regime=candidate_data.get("regime_label"),
                    gate_result=v23_gate_result,
                    block_reason=", ".join(v23_gate_result.get("reasons", [])),
                    rsi_result=v23_gate_result.get("metadata", {}).get("rsi_value"),
                    data_status=candidate_data.get("data_status"),
                    created_at=datetime.datetime.now(timezone.utc),
                    evaluation_timestamp=candidate_data.get("eval_time")
                )

                db.add(shadow_rec)
                db.commit()
                print(f"[Shadow] Recorded V2.3 Decision: {v23_decision} for {candidate_data.get('symbol')} (Gate: {v23_gate_result['decision']})")
            except Exception as e:
                print(f"[Shadow] Failed to record decision: {e}")
                db.rollback()
