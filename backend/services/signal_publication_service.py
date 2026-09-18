import datetime
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, LiveSignalDB
from backend.services.signal_validator_service import SignalValidatorService

class SignalPublicationService:
    """
    Operational Signal Publication Workflow.
    Manages the transition from GENERATED to PUBLISHED.
    """

    @staticmethod
    async def publish_pending_signals():
        """
        Scans Neon for DRAFT/GENERATED signals and validates them for production.
        """
        with SessionLocal() as session:
            # For now, Strategy V2.2 publishes immediately if valid
            pending = session.query(LiveSignalDB).filter(LiveSignalDB.status == "GENERATED").all()

            published_count = 0
            for sig in pending:
                # 1. Forensic Validation Gate
                from backend.services.signal_ledger_service import SignalLedgerService
                domain_sig = await SignalLedgerService.get_signal(sig.id)

                if not domain_sig: continue

                validation = SignalValidatorService.validate_publication(domain_sig)

                if validation["is_valid"]:
                    sig.status = "WAITING_FOR_ENTRY"
                    sig.updated_at = datetime.datetime.utcnow()
                    published_count += 1
                    print(f"[Publication] Signal {sig.id} ({sig.symbol}) PUBLISHED.")
                else:
                    sig.status = "REJECTED"
                    sig.rejection_reason = "; ".join(validation["issues"])
                    print(f"[Publication] Signal {sig.id} ({sig.symbol}) REJECTED: {sig.rejection_reason}")

            session.commit()
            return published_count
