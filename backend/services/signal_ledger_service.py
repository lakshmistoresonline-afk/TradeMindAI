import os
import datetime
from datetime import timezone
import uuid
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.core.postgres import LiveSignalDB, ShadowSignalDB, SessionLocal
from backend.core.database import db_client
from backend.domain.models.ios import LiveSignal
from backend.core.container import container
from backend.services.signal_eligibility import is_eligible_buy

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        import datetime
        import pandas as pd
        if isinstance(obj, (datetime.datetime, datetime.date, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)

class SignalLedgerService:
    """
    Authoritative Signal Ledger Service (Atomic Idempotency & BUY-Only Enforced).
    Neon/Postgres is the authority. Firestore is a mirror.
    """

    @staticmethod
    async def _create_signal_internal(signal: LiveSignal, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Internal implementation of atomic signal creation & persistence outcome mapping.
        Distinguishes PERSISTED, DUPLICATE_PREVENTED, REJECTED_NON_BUY, and PERSISTENCE_FAILED.
        """
        if not is_eligible_buy(signal):
            return {
                "status": "REJECTED_NON_BUY",
                "signal": None,
                "inserted": False,
                "duplicate_reason": "INELIGIBLE_RATING_OR_STATUS",
                "error_detail": "Signal violates BUY-only eligibility policy and cannot be persisted.",
                "mirror_status": "SKIPPED"
            }

        if "PYTEST_CURRENT_TEST" in os.environ and session is None:
            raise RuntimeError("Unisolated database session detected during pytest execution! Explicit test session fixture is required.")

        is_caller_session = session is not None
        db = session or SessionLocal()
        norm_symbol = signal.symbol.strip().upper()
        try:
            tf = getattr(signal, "timeframe", None)
            if not tf and hasattr(signal, "decision") and signal.decision:
                tf = getattr(signal.decision, "timeframe", "SWING")
            if not tf:
                tf = "SWING"

            # Check Phase 9.4.3 Global Uniqueness Invariant: Enforce at most 1 active signal per stock symbol globally
            existing = db.query(LiveSignalDB).filter(
                LiveSignalDB.symbol == norm_symbol,
                LiveSignalDB.status == "ACTIVE"
            ).first()
            if existing:
                mapped_existing = container.ios_repo._map_db_to_live_signal(existing)
                return {
                    "status": "DUPLICATE_PREVENTED",
                    "signal": mapped_existing,
                    "inserted": False,
                    "duplicate_reason": f"ACTIVE_SIGNAL_EXISTS_FOR_SYMBOL: {norm_symbol} (existing_id: {existing.id})",
                    "error_detail": None,
                    "mirror_status": "SKIPPED"
                }

            # 1. Authoritative Database Insertion (Neon/Postgres)
            signal_data = signal.model_dump()
            db_signal = LiveSignalDB(
                id=signal.id,
                symbol=norm_symbol,
                direction=getattr(signal, "direction", "LONG"),
                rating=getattr(signal, "rating", "BUY"),
                timeframe=tf,
                status=signal.status,
                entry_price=getattr(signal, "entry_price", None),
                target_price=getattr(signal, "target_price", None),
                stop_price=getattr(signal, "stop_price", None),
                confidence=getattr(signal, "confidence", getattr(signal, "conviction", 0.0)),
                created_at=getattr(signal, "created_at", datetime.datetime.now(timezone.utc))
            )
            db.add(db_signal)

            if is_caller_session:
                db.flush()
                db.refresh(db_signal)
                status_code = "PENDING_CALLER_COMMIT"
            else:
                db.commit()
                db.refresh(db_signal)
                status_code = "PERSISTED_AND_COMMITTED"

            mapped_inserted = container.ios_repo._map_db_to_live_signal(db_signal)

            # 2. Firestore Secondary Mirroring (Deferred for caller sessions, non-blocking for internal committed sessions)
            mirror_status = "DEFERRED_UNTIL_CALLER_COMMIT" if is_caller_session else "SKIPPED"
            if not is_caller_session:
                try:
                    if db_client:
                        fs_doc = db_client.collection("signals").document(signal.id)
                        json_safe_data = json.loads(json.dumps(signal_data, cls=CustomJSONEncoder))
                        fs_doc.set(json_safe_data)
                        mirror_status = "SUCCESS"
                except Exception as fs_ex:
                    mirror_status = "FAILED"
                    print(f"[SignalLedger] Non-fatal Firestore mirror warning: {fs_ex}")

            return {
                "status": status_code,
                "signal": mapped_inserted,
                "inserted": True,
                "duplicate_reason": None,
                "error_detail": None,
                "mirror_status": mirror_status
            }
        except IntegrityError:
            if not is_caller_session:
                db.rollback()
            existing_after_race = db.query(LiveSignalDB).filter(
                LiveSignalDB.symbol == norm_symbol,
                LiveSignalDB.status == "ACTIVE"
            ).first()
            if existing_after_race:
                mapped_race = container.ios_repo._map_db_to_live_signal(existing_after_race)
                return {
                    "status": "DUPLICATE_PREVENTED",
                    "signal": mapped_race,
                    "inserted": False,
                    "duplicate_reason": f"CONCURRENT_UNIQUE_CONFLICT: {norm_symbol}",
                    "error_detail": None,
                    "mirror_status": "SKIPPED"
                }
            raise
        except Exception as ex:
            if not is_caller_session:
                db.rollback()
            raise ex
        finally:
            if not is_caller_session:
                db.close()

    @staticmethod
    async def create_signal(signal: LiveSignal, session: Optional[Session] = None) -> LiveSignal:
        """
        Atomically creates a signal in Neon and mirrors to Firestore.
        Enforces BUY-only eligibility and Phase 9.4.3 Global Uniqueness Invariant.
        Returns the authoritative LiveSignal instance.
        """
        res = await SignalLedgerService._create_signal_internal(signal, session=session)
        if res["status"] == "REJECTED_NON_BUY":
            raise ValueError(res.get("error_detail", "Signal violates BUY-only eligibility policy."))
        if res["status"] == "PERSISTENCE_FAILED":
            raise RuntimeError(res.get("error_detail", "Persistence failed."))
        return res["signal"]

    @staticmethod
    async def mirror_signal_after_commit(signal: LiveSignal) -> Dict[str, Any]:
        """
        Secondary Firestore Mirroring helper (Runs ONLY after caller transaction commit succeeds).
        Does NOT commit or alter caller database transactions.
        """
        mirror_status = "SKIPPED"
        try:
            if db_client:
                signal_data = signal.model_dump()
                fs_doc = db_client.collection("signals").document(signal.id)
                json_safe_data = json.loads(json.dumps(signal_data, cls=CustomJSONEncoder))
                fs_doc.set(json_safe_data)
                mirror_status = "SUCCESS"
        except Exception as fs_ex:
            mirror_status = "FAILED"
            print(f"[SignalLedger] Post-commit Firestore mirror warning: {fs_ex}")

        return {
            "status": "MIRRORED",
            "signal_id": signal.id,
            "mirror_status": mirror_status
        }

    @staticmethod
    async def persist_signal(signal: LiveSignal, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Persists candidate signal to ledger cleanly, returning status dictionary for service scan funnel accounting.
        Distinguishes PERSISTED, DUPLICATE_PREVENTED, REJECTED_NON_BUY, and PERSISTENCE_FAILED.
        """
        try:
            return await SignalLedgerService._create_signal_internal(signal, session=session)
        except Exception as ex:
            return {
                "status": "PERSISTENCE_FAILED",
                "signal": None,
                "inserted": False,
                "duplicate_reason": None,
                "error_detail": str(ex),
                "mirror_status": "FAILED"
            }

    @staticmethod
    async def update_signal(signal_id: str, updates: Dict[str, Any], session: Optional[Session] = None) -> bool:
        """
        Updates a signal in Neon/Postgres while strictly preserving caller transaction ownership.
        Caller-owned sessions execute `db.flush()` and `db.refresh()`, leaving `commit()` to the caller.
        Internally created sessions execute `db.commit()` and `db.close()`.
        Returns True on success, False if signal not found, blocked by immutability rules, or on error.
        """
        is_caller_session = session is not None
        db = session if session is not None else SessionLocal()
        try:
            db_signal = db.query(LiveSignalDB).filter(LiveSignalDB.id == signal_id).first()
            if not db_signal:
                return False

            TERMINAL_STATES = ["TARGET_HIT", "STOP_LOSS", "EXPIRED", "CANCELLED", "AMBIGUOUS"]

            # 1. Reopen protection: Reject updates attempting to change status from terminal back to non-terminal
            if db_signal.status in TERMINAL_STATES:
                new_status = updates.get("status")
                if new_status and new_status not in TERMINAL_STATES:
                    print(f"[SignalLedger] Update BLOCKED: Cannot reopen terminal signal {signal_id} (status: {db_signal.status} -> {new_status}).")
                    return False

            # 2. Immutability protection on core strategy facts & lineage fields
            RESTRICTED_FIELDS = [
                "symbol", "direction", "asset_type", "asset_class", "instrument_id",
                "entry_price", "target_price", "stop_price", "profit_pct",
                "outcome_date", "exit_price", "realized_return",
                "decision_timestamp", "strategy_version", "signal_version",
                "model_id", "model_version", "model_hash",
                "feature_version", "feature_hash", "prediction_id", "provenance_id", "decision_hash"
            ]

            # If signal is already terminal, block changes to any restricted fields
            if db_signal.status in TERMINAL_STATES:
                for key in updates:
                    if key in RESTRICTED_FIELDS:
                        print(f"[SignalLedger] Update BLOCKED: Signal {signal_id} is in terminal state {db_signal.status}. Cannot mutate field: {key}")
                        return False

            # If transitioning to terminal, block simultaneous modification of core strategy entry facts
            proposed_status = updates.get("status")
            if proposed_status in TERMINAL_STATES and db_signal.status not in TERMINAL_STATES:
                CORE_ENTRY_FACTS = ["entry_price", "symbol", "direction", "strategy_version", "model_version", "prediction_id"]
                for key in updates:
                    if key in CORE_ENTRY_FACTS:
                        print(f"[SignalLedger] Update BLOCKED: Cannot mutate core entry fact {key} during terminal transition.")
                        return False

            # Check unknown fields
            for k in updates:
                if not hasattr(db_signal, k) and k not in ("asset_class", "profit_pct", "outcome_date", "realized_return", "decision_hash"):
                    print(f"[SignalLedger] Update BLOCKED: Unknown field {k} supplied.")
                    return False

            for k, v in updates.items():
                if hasattr(db_signal, k):
                    if k in ["provenance", "events"] and isinstance(v, (dict, list)):
                        setattr(db_signal, k, json.dumps(v))
                    else:
                        setattr(db_signal, k, v)

            db_signal.updated_at = datetime.datetime.now(timezone.utc)

            if is_caller_session:
                db.flush()
                db.refresh(db_signal)
            else:
                db.commit()
                db.refresh(db_signal)

            return True
        except Exception as ex:
            if not is_caller_session:
                db.rollback()
            return False
        finally:
            if not is_caller_session:
                db.close()

    @staticmethod
    async def get_signal(signal_id: str, session: Optional[Session] = None) -> Optional[LiveSignal]:
        db = session or SessionLocal()
        try:
            db_signal = db.query(LiveSignalDB).filter(LiveSignalDB.id == signal_id).first()
            if not db_signal:
                return None
            return container.ios_repo._map_db_to_live_signal(db_signal)
        finally:
            if session is None:
                db.close()
