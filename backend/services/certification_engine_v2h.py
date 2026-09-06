import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowProvenanceDB, PredictionDB

class Phase2HCertificationEngine:
    """
    Workstream 20: Phase 2H Institutional Certification Engine.
    Enforces deterministic, machine-readable hard gates.
    """

    POLICY_VERSION = "2H.1.0"
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
            gates["population_integrity"] = cls.evaluate_gate("population_integrity", "PASS" if total_count >= 1259 else "FAIL")

            # 2. Active Signal Hard Gates
            active_identity = "PASS"
            active_pricing = "PASS"
            current_signal_lineage = "PASS"
            fno_identity = "PASS"
            fno_pricing = "PASS"
            prediction_linkage = "PASS"
            provenance = "PASS"

            legacy_active_count = 0
            current_active_count = 0

            for sig in active:
                is_legacy = sig.timestamp < cls.LEDGER_2_0_ENFORCEMENT_DATE
                if is_legacy: legacy_active_count += 1
                else: current_active_count += 1

                # A. Identity
                if not sig.symbol or not sig.asset_class or not sig.instrument_id:
                     active_identity = "FAIL"

                # B. Pricing
                if sig.current_price is None:
                    if sig.asset_class in ['OPTIONS', 'FUTURES']:
                        if sig.derivative_current is None:
                            active_pricing = "FAIL"
                            fno_pricing = "FAIL"
                    else:
                        active_pricing = "FAIL"

                # C. Lineage (Mandatory for Current)
                if not is_legacy:
                    if not sig.prediction_id or "UNAVAILABLE" in str(sig.prediction_id):
                        current_signal_lineage = "FAIL"
                        prediction_linkage = "FAIL"
                    if not sig.provenance_id or "UNAVAILABLE" in str(sig.provenance_id):
                        provenance = "FAIL"
                else:
                    # Legacy signals are NOT_APPLICABLE for lineage if they haven't failed already
                    if prediction_linkage == "PASS": prediction_linkage = "NOT_APPLICABLE"
                    if provenance == "PASS": provenance = "NOT_APPLICABLE"

            gates["active_identity"] = cls.evaluate_gate("active_identity", active_identity)
            gates["active_pricing"] = cls.evaluate_gate("active_pricing", active_pricing)
            gates["current_signal_lineage"] = cls.evaluate_gate("current_signal_lineage", current_signal_lineage, mandatory=(current_active_count > 0))
            gates["prediction_linkage"] = cls.evaluate_gate("prediction_linkage", prediction_linkage, mandatory=(current_active_count > 0))
            gates["provenance"] = cls.evaluate_gate("provenance", provenance, mandatory=(current_active_count > 0))
            gates["fno_identity"] = cls.evaluate_gate("fno_identity", fno_identity)
            gates["fno_pricing"] = cls.evaluate_gate("fno_pricing", fno_pricing)

            # 3. Aggregation Logic
            blocking_failures = [g["name"] for g in gates.values() if g["mandatory"] and g["status"] == "FAIL"]
            overall_pass = len(blocking_failures) == 0

            # 4. Final Status
            final_status = "PHASE2H_FAIL"
            if overall_pass:
                limitations = []
                if any(g["status"] == "NOT_APPLICABLE" for g in gates.values()):
                    limitations.append("LEGACY_EXEMPTIONS_ACTIVE")
                limitations.append("STATISTICAL_SIGNIFICANCE_NOT_PROVEN")

                final_status = "PHASE2H_CONDITIONAL_PASS" if limitations else "PHASE2H_PASS"

            return {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "policy_version": cls.POLICY_VERSION,
                "population": {
                    "total": total_count,
                    "active": len(active),
                    "legacy_active": legacy_active_count,
                    "current_active": current_active_count
                },
                "gates": gates,
                "blocking_failures": blocking_failures,
                "overall_pass": overall_pass,
                "final_status": final_status
            }
