import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowProvenanceDB, PredictionDB
from backend.domain.models.ios import LiveSignal

class Phase2FCertificationEngine:
    """
    Workstream 20: Institutional Certification Engine.
    Enforces deterministic, machine-readable hard gates for signal validation.
    Eliminates narrative overrides and false-pass contradictions.
    """

    POLICY_VERSION = "2F.1.0"
    LEDGER_2_0_ENFORCEMENT_DATE = datetime.datetime(2026, 9, 4, 12, 0, 0)

    @staticmethod
    def evaluate_gate_status(name: str, value: Any, mandatory: bool = True) -> Dict[str, Any]:
        status = "PASS" if value else "FAIL"

        # Semantic mapping for different types of "not passing"
        if value is None or value == "MISSING":
            status = "FAIL"
        elif value == "NOT_APPLICABLE":
            status = "NOT_APPLICABLE"

        return {
            "name": name,
            "status": status,
            "mandatory": mandatory,
            "blocking": mandatory
        }

    @classmethod
    async def run_certification_audit(cls) -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. Fetch Authoritative Population
            active = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
            total_count = session.query(ShadowSignalDB).count()

            # 2. Evaluate Individual Gates
            gates = {}

            # Population Integrity
            gates["population_integrity"] = cls.evaluate_gate_status("population_integrity", total_count == 1259)

            # Active Signal Hard Gates
            active_identity = True
            active_pricing = True
            linkage_pass = True
            fno_identity = True

            for sig in active:
                # Origin Check
                is_legacy = sig.timestamp < cls.LEDGER_2_0_ENFORCEMENT_DATE

                # A. Identity
                if not sig.symbol or not sig.asset_class: active_identity = False

                # B. Pricing (Institutional Rule: No fallback to Entry)
                if sig.current_price is None:
                    # If F&O, we need derivative price
                    if sig.asset_class in ['OPTIONS', 'FUTURES']:
                        if sig.derivative_current is None: active_pricing = False
                    else:
                        active_pricing = False

                # C. Linkage
                if not is_legacy:
                    if sig.prediction_id is None or sig.provenance_id is None:
                        linkage_pass = False

                # D. F&O Identity
                if sig.asset_class in ['OPTIONS', 'FUTURES']:
                    if not sig.instrument_id or not sig.derivative_symbol or not sig.expiry:
                        fno_identity = False

            gates["active_identity"] = cls.evaluate_gate_status("active_identity", active_identity)
            gates["active_pricing"] = cls.evaluate_gate_status("active_pricing", active_pricing)
            gates["prediction_linkage"] = cls.evaluate_gate_status("prediction_linkage", linkage_pass)
            gates["fno_identity"] = cls.evaluate_gate_status("fno_identity", fno_identity)

            # 3. Aggregation Logic (Mathematical Assertion)
            blocking_failures = [g["name"] for g in gates.values() if g["blocking"] and g["status"] == "FAIL"]

            overall_pass = len(blocking_failures) == 0

            # 4. Final Status Determination
            final_status = "PHASE2F_FAIL"
            if overall_pass:
                # Check for non-blocking limitations (e.g. legacy records missing linkage)
                limitations = []
                legacy_linkage_missing = any(s.prediction_id is None for s in active if s.timestamp < cls.LEDGER_2_0_ENFORCEMENT_DATE)
                if legacy_linkage_missing:
                    limitations.append("LEGACY_LINKAGE_UNAVAILABLE")

                final_status = "PHASE2F_CONDITIONAL_PASS" if limitations else "PHASE2F_PASS"

            result = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "policy_version": cls.POLICY_VERSION,
                "gates": gates,
                "blocking_failures": blocking_failures,
                "overall_pass": overall_pass,
                "final_status": final_status
            }

            return result
