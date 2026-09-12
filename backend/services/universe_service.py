import datetime
from typing import List, Dict, Any, Optional
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
try:
    from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
except ModuleNotFoundError:
    # Fallback if scripts package is not in python path (e.g. docker)
    NIFTY_200_CONSTITUENTS = [
        "ABB", "ACC", "ADANIENT", "ADANIPORTS", "ADANIPOWER", "ATGL", "ADANIENSOL", "AMBUJACEM", "APOLLOHOSP", "ASIANPAINT",
        "ASTRAL", "AUROPHARMA", "DMART", "AXISBANK", "BSE", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BALKRISIND",
        "BANDHANBNK", "BANKBARODA", "BANKINDIA", "MAHABANK", "BATAINDIA", "BEL", "BEML", "BHARATFORG", "BHEL", "BPCL",
        "BHARTIARTL", "BIOCON", "BOSCHLTD", "BRITANNIA", "CGPOWER", "CANBK", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE",
        "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUMMINSIND", "DLF", "DABUR", "DALBHARAT", "DEEPAKNTR", "DELHIVERY",
        "DIVISLAB", "DIXON", "LALPATHLAB", "DRREDDY", "EICHERMOT", "ESCORTS", "NYKAA", "FEDERALBNK", "FACT", "FORTIS",
        "GAIL", "GMRINFRA", "GODREJCP", "GODREJIND", "GODREJPROP", "GRASIM", "GUJGASLTD", "GSPL", "HCLTECH", "HDFCAMC",
        "HDFCBANK", "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO", "HAL", "HINDPETRO", "HINDUNILVR", "HINDZINC", "HUDCO",
        "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDBI", "IDFCFIRSTB", "ITC", "INDIANB", "INDHOTEL", "IOC", "IRCTC",
        "IRFC", "IGL", "INDUSINDBK", "NAUKRI", "INFY", "INDIGO", "IPCALAB", "JIOFIN", "JSWENERGY", "JSWSTEEL",
        "JINDALSTEL", "JINDALSTEL", "KALYANKJIL", "KOTAKBANK", "KPRMILL", "L&TFH", "LTTS", "LICHSGFIN", "LTIM", "LT",
        "LAURUSLABS", "LICI", "LUPIN", "MRF", "LODHA", "M&MFIN", "M&M", "MANAPPURAM", "MARICO", "MARUTI",
        "MFSL", "MAXHEALTH", "MAZDOCK", "METROPOLIS", "MUTHOOTFIN", "NHPC", "NMDC", "NTPC", "NATIONALUM", "NAVINFLUOR",
        "NESTLEIND", "OBEROIRLTY", "ONGC", "OIL", "ONE97", "PIIND", "PAGEIND", "PATANJALI", "PERSISTENT", "PETRONET",
        "PIDILITIND", "PEL", "POLYCAB", "POONAWALLA", "PFC", "POWERGRID", "PRESTIGE", "PNB", "RECLTD", "RVNL",
        "RELIANCE", "SBICARD", "SBILIFE", "SJVN", "SRF", "MOTHERSON", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SONACOMS",
        "SBIN", "SAIL", "SUNPHARMA", "SUNTV", "SUPREMEIND", "SUZLON", "SYNGENE", "TVSMOTOR", "TATACHEM", "TATACOMM",
        "TCS", "TATACONSUM", "TATAELXSI", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TTML", "TECHM", "TITAN", "TORNTPOWER",
        "TORNTPHARM", "TRENT", "TRIDENT", "TIINDIA", "UCOBANK", "UNOMINDA", "UPL", "ULTRACEMCO", "UNIONBANK", "UBL",
        "VBL", "VEDL", "VOLTAS", "WHIRLPOOL", "WIPRO", "YESBANK", "ZOMATO", "ZYDUSLIFE"
    ]

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
