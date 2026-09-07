import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowProvenanceDB, PredictionDB

class Phase2JCertificationEngine:
    """
    Workstream 20/33: Phase 2J Institutional Certification Engine.
    Enforces context-aware hard gates (Legacy vs Current).
    Ensures 100% field completeness for post-Ledger signals, including Decision Trace.
    """

    POLICY_VERSION = "2J.1.0"
    LEDGER_2_0_ENFORCEMENT_DATE = datetime.datetime(2026, 9, 4, 12, 0, 0)

    @staticmethod
    def evaluate_gate(name: str, status: str, mandatory: bool = True, reason: Optional[str] = None) -> Dict[str, Any]:
        return {
            "name": name,
            "status": status, # PASS, FAIL, NOT_APPLICABLE
            "mandatory": mandatory,
            "blocking": mandatory and status == "FAIL",
            "reason": reason
        }

    @classmethod
    async def run_certification_audit(cls) -> Dict[str, Any]:
        with SessionLocal() as session:
            active = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
            total_count = session.query(ShadowSignalDB).count()

            gates = {}

            # 1. Population Integrity
            gates["population_integrity"] = cls.evaluate_gate("population_integrity", "PASS" if total_count >= 1260 else "FAIL")

            # 2. Current Signal Integrity (Workstream 23/28)
            current_signals = [s for s in active if s.timestamp >= cls.LEDGER_2_0_ENFORCEMENT_DATE]

            current_integrity = "PASS"
            if not current_signals:
                current_integrity = "NOT_APPLICABLE"
            else:
                for s in current_signals:
                    # Mandatory fields for current signals (Zero-Gap Requirement)
                    mandatory_fields = [
                        s.prediction_id, s.provenance_id, s.feature_version, s.regime,
                        s.stop_price, s.risk_reward_ratio, s.asset_type,
                        s.decision_id, s.model_run_id, s.market_snapshot_id, s.feature_snapshot_id,
                        s.signal_timestamp
                    ]
                    if any(f is None or "UNAVAILABLE" in str(f) for f in mandatory_fields):
                        current_integrity = "FAIL"
                        break

            gates["current_signal_integrity"] = cls.evaluate_gate("current_signal_integrity", current_integrity)

            # 3. Active Pricing & Identity (Global active set)
            active_identity = "PASS"
            active_pricing = "PASS"
            fno_identity = "PASS"
            fno_pricing = "PASS"

            for sig in active:
                # Identity
                if not sig.symbol or not sig.asset_class or not sig.instrument_id:
                     active_identity = "FAIL"

                # Pricing
                if sig.current_price is None:
                    if sig.asset_class in ['OPTIONS', 'FUTURES']:
                        if sig.derivative_current is None:
                            active_pricing = "FAIL"
                            fno_pricing = "FAIL"
                    else:
                        active_pricing = "FAIL"

                # F&O Identity
                if sig.asset_class in ['OPTIONS', 'FUTURES']:
                    if not sig.derivative_symbol or not sig.expiry:
                        fno_identity = "FAIL"

            gates["active_identity"] = cls.evaluate_gate("active_identity", active_identity)
            gates["active_pricing"] = cls.evaluate_gate("active_pricing", active_pricing)
            gates["fno_identity"] = cls.evaluate_gate("fno_identity", fno_identity)
            gates["fno_pricing"] = cls.evaluate_gate("fno_pricing", fno_pricing)

            # 4. Global Integrity
            violations = session.query(ShadowSignalDB).filter(ShadowSignalDB.data_timestamp > ShadowSignalDB.timestamp).count()
            gates["temporal_isolation"] = cls.evaluate_gate("temporal_isolation", "PASS" if violations == 0 else "FAIL")

            # 5. Aggregation Logic (Hard Gate)
            blocking_failures = [g["name"] for g in gates.values() if g["blocking"] and g["status"] == "FAIL"]
            overall_pass = len(blocking_failures) == 0

            # 6. Final Status Determination
            final_status = "PHASE2J_FAIL"
            if overall_pass:
                limitations = []
                if gates["current_signal_integrity"]["status"] == "NOT_APPLICABLE":
                    limitations.append("NO_CURRENT_SIGNALS_OBSERVED")
                limitations.append("STATISTICAL_SIGNIFICANCE_NOT_PROVEN")

                final_status = "PHASE2J_CONDITIONAL_PASS" if limitations else "PHASE2J_PASS"

            return {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "policy_version": cls.POLICY_VERSION,
                "gates": gates,
                "blocking_failures": blocking_failures,
                "overall_pass": overall_pass,
                "final_status": final_status,
                "summary": {
                    "total_active": len(active),
                    "current_active": len(current_signals),
                    "legacy_active": len(active) - len(current_signals)
                }
            }
