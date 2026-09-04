import datetime
from typing import List, Dict, Any, Optional
from backend.core.postgres import SessionLocal, InstrumentDB, StockDB

class FNORegistryService:
    """
    Workstream 13: F&O Contract Registry.
    Tracks contract lifecycle: ELIGIBLE -> DISCOVERED -> PRICED.
    """

    @staticmethod
    async def get_fno_registry_status() -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. Eligible
            eligible = session.query(StockDB).filter(StockDB.is_fno == True).count()

            # 2. Discovered
            discovered_res = session.query(InstrumentDB.underlying_symbol).distinct().all()
            discovered_symbols = {r[0] for r in discovered_res}

            # 3. Priced (Last 5 mins)
            # Placeholder for price staleness check
            priced = len(discovered_symbols) # Mock for now

            return {
                "eligible_underlyings": eligible,
                "discovered_underlyings": len(discovered_symbols),
                "priced_underlyings": priced,
                "total_contracts": session.query(InstrumentDB).count(),
                "provider": "YAHOO_FINANCE (Limited)"
            }

    @staticmethod
    async def get_contracts_for_underlying(symbol: str) -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            res = session.query(InstrumentDB).filter(InstrumentDB.underlying_symbol == symbol).all()
            return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in res]
