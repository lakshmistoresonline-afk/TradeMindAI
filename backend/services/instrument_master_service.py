import os
import json
import pandas as pd
import datetime
from typing import Dict, Any, List, Optional
from backend.core.config import settings

class InstrumentMasterService:
    """
    Workstream 8: Production-grade Instrument Master.
    Handles indexing exchange-certified identifiers from the Neon InstrumentDB.
    """

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._last_refresh = None
        self._status = "READY" # Database is always there

    async def refresh_master(self) -> Dict[str, Any]:
        """
        Updates metadata regarding the last database sync.
        """
        from backend.core.postgres import SessionLocal, InstrumentDB
        from sqlalchemy import func

        with SessionLocal() as session:
            count = session.query(InstrumentDB).filter(InstrumentDB.source == self.provider_name).count()
            latest = session.query(func.max(InstrumentDB.last_updated)).filter(InstrumentDB.source == self.provider_name).scalar()

            self._last_refresh = latest

            if count == 0:
                self._status = "CONFIGURATION_REQUIRED"
                reason = f"No instruments found in Neon for provider {self.provider_name}. Sync required."
            else:
                self._status = "READY"
                reason = "Neon Instrument Master is synchronized."

        return {
            "status": self._status,
            "provider": self.provider_name,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "record_count": count,
            "reason": reason
        }

    async def resolve_fno_contract(self, symbol: str, expiry: datetime.datetime, strike: float = None, option_type: str = None) -> Dict[str, Any]:
        """
        Resolves TradeMind identity to provider-specific numerical IDs or keys.
        """
        from backend.core.postgres import SessionLocal, InstrumentDB
        from sqlalchemy import and_

        with SessionLocal() as session:
            query = session.query(InstrumentDB).filter(
                InstrumentDB.underlying_symbol == symbol,
                InstrumentDB.source == self.provider_name
            )

            # Match Expiry (handling date-only comparison if needed)
            if expiry:
                 # Search within the same day
                 start_of_day = expiry.replace(hour=0, minute=0, second=0, microsecond=0)
                 end_of_day = expiry.replace(hour=23, minute=59, second=59, microsecond=999999)
                 query = query.filter(InstrumentDB.expiry.between(start_of_day, end_of_day))

            if strike is not None:
                query = query.filter(InstrumentDB.strike == strike)

            if option_type:
                query = query.filter(InstrumentDB.option_type == option_type)

            res = query.all()

            if len(res) == 0:
                return {"status": "NOT_FOUND"}
            if len(res) > 1:
                return {"status": "AMBIGUOUS", "matches": [r.id for r in res]}

            match = res[0]
            return {
                "status": "RESOLVED",
                "provider_id": match.id,
                "trading_symbol": match.trading_symbol,
                "instrument_type": match.instrument_type,
                "lot_size": match.lot_size
            }

    @property
    def audit_metadata(self) -> Dict[str, Any]:
        return {
            "version": "1.1",
            "provider": self.provider_name,
            "status": self._status,
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None
        }
