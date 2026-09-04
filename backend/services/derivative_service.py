import datetime
from typing import List, Dict, Any, Optional
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider

class DerivativeService:
    """
    Workstream 3: F&O Contract Discovery and Registry.
    Implements separation between ELIGIBLE, DISCOVERED, and PRICED.
    """
    def __init__(self, repository: IStockRepository, provider: IMarketDataProvider):
        self.repository = repository
        self.provider = provider

    async def sync_contracts(self, underlying_symbol: str) -> Dict[str, Any]:
        """
        Discovers and persists Near/Next/Far contracts for an underlying.
        """
        # 1. Check Eligibility
        stock = await self.repository.get_stock_by_symbol(underlying_symbol)
        if not stock or not stock.is_fno:
            return {"status": "BLOCKED", "reason": "NOT_FNO_ELIGIBLE"}

        # 2. Discover Expiries
        expiries = await self.provider.get_expiries(underlying_symbol)
        if not expiries:
            return {"status": "FAILED", "reason": "NO_EXPIRIES_FOUND"}

        # 3. Near/Next/Far promotion
        expiries = sorted(expiries)[:3]

        instruments_to_save = []
        for i, expiry in enumerate(expiries):
            label = ["NEAR", "NEXT", "FAR"][i]
            # Futures
            fut_id = f"{underlying_symbol}_{expiry.strftime('%y%b').upper()}_FUT"
            instruments_to_save.append({
                "id": fut_id,
                "exchange": "NSE",
                "trading_symbol": f"{underlying_symbol}{expiry.strftime('%y%b').upper()}FUT",
                "segment": "FUTURES",
                "instrument_type": "FUTSTK" if underlying_symbol not in ["NIFTY", "BANKNIFTY"] else "FUTIDX",
                "underlying_symbol": underlying_symbol,
                "expiry": expiry,
                "source": self.provider.__class__.__name__,
                "last_updated": datetime.datetime.utcnow()
            })

        await self.repository.save_instruments(instruments_to_save)
        return {"status": "SUCCESS", "contract_count": len(instruments_to_save)}

    async def audit_derivative_coverage(self) -> Dict[str, Any]:
        """
        Reports on the status of derivative discovery.
        """
        eligible_stocks = await self.repository.get_all_stocks(limit=500)
        eligible_symbols = [s.symbol for s in eligible_stocks if s.is_fno]

        discovered = await self.repository.get_instruments()
        discovered_underlyings = {i['underlying_symbol'] for i in discovered}

        return {
            "eligible_underlyings": len(eligible_symbols),
            "discovered_underlyings": len(discovered_underlyings),
            "total_contracts": len(discovered),
            "coverage_pct": round(len(discovered_underlyings) / len(eligible_symbols) * 100, 2) if eligible_symbols else 0
        }
