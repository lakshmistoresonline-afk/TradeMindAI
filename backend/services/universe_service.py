import datetime
from typing import List, Dict, Any, Optional
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

class UniverseService:
    """
    Workstream 1: NIFTY 200 Production Universe Management.
    Ensures exactly 200 constituents are monitored with explicit states.
    """
    NIFTY_200_CONSTITUENTS = NIFTY_200_CONSTITUENTS

    def __init__(self, repository: IStockRepository, provider: IMarketDataProvider):
        self.repository = repository
        self.provider = provider
        self.universe_version = "NIFTY_200_AUG2026"

    async def audit_universe_readiness(self) -> Dict[str, Any]:
        """
        Performs a full audit of all 200 symbols for production readiness.
        """
        all_stocks = await self.repository.get_all_stocks(limit=500)
        stock_map = {s.symbol: s for s in all_stocks}

        readiness = {
            "total": len(NIFTY_200_CONSTITUENTS),
            "fresh": 0,
            "stale": 0,
            "unavailable": 0,
            "blocked": 0,
            "details": []
        }

        now = datetime.datetime.utcnow()

        for symbol in NIFTY_200_CONSTITUENTS:
            stock = stock_map.get(symbol)

            status = "ACTIVE"
            freshness = "UNKNOWN"
            reason = None

            if not stock:
                status = "SIGNAL_BLOCKED"
                freshness = "UNAVAILABLE"
                reason = "NOT_FOUND_IN_REGISTRY"
                readiness["unavailable"] += 1
            else:
                # 1. Price check
                if stock.last_price is None:
                    status = "SIGNAL_BLOCKED"
                    freshness = "UNAVAILABLE"
                    reason = "PRICE_MISSING"
                    readiness["unavailable"] += 1
                else:
                    # 2. Freshness check (24h threshold)
                    age_hours = (now - stock.updated_at).total_seconds() / 3600.0 if stock.updated_at else 999.0
                    if age_hours < 24:
                        freshness = "FRESH"
                        readiness["fresh"] += 1
                    else:
                        freshness = "STALE"
                        reason = f"Data age: {age_hours:.1f}h"
                        readiness["stale"] += 1

            if status == "SIGNAL_BLOCKED":
                readiness["blocked"] += 1

            readiness["details"].append({
                "symbol": symbol,
                "status": status,
                "freshness": freshness,
                "reason": reason,
                "last_updated": stock.updated_at if stock else None
            })

        return readiness

    async def sync_universe(self):
        """
        Bootstrap/Sync: Ensures all canonical constituents are in the DB.
        """
        all_stocks = await self.repository.get_all_stocks(limit=500)
        existing_symbols = {s.symbol for s in all_stocks}

        added = 0
        for symbol in NIFTY_200_CONSTITUENTS:
            if symbol not in existing_symbols:
                from backend.domain.models.stock import Stock
                new_stock = Stock(
                    symbol=symbol,
                    name=f"{symbol} Limited",
                    index_membership="NIFTY_200",
                    universe_version=self.universe_version,
                    ai_status="READY"
                )
                await self.repository.save_stock(new_stock)
                added += 1

        return {"status": "SUCCESS", "added": added}
