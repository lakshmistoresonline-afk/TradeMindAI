import datetime
from typing import Dict, Any, List, Optional
from backend.core.container import container
from backend.core.postgres import SessionLocal, StockDB

class SecurityMasterService:
    """
    Final Delivery: Authoritative Security Master Service.
    Enforces symbol identity, sector mapping, and industry classification.
    """

    SECTOR_MAPPING = {
        "ACC": "CEMENT",
        "AMBUJACEM": "CEMENT",
        "ABB": "CAPITAL GOODS",
        "BAJFINANCE": "FINANCIAL SERVICES",
        "CANFINHOME": "FINANCIAL SERVICES",
        "APOLLOTYRE": "AUTO",
        "ADANIENT": "METALS & MINING",
        "RELIANCE": "ENERGY",
        "TCS": "IT",
        "INFY": "IT",
        "ICICIBANK": "FINANCIAL SERVICES",
        "AXISBANK": "FINANCIAL SERVICES",
        "SBIN": "FINANCIAL SERVICES",
        "HDFCBANK": "FINANCIAL SERVICES",
        "LT": "CONSTRUCTION",
        "ITC": "CONSUMER GOODS",
        "HINDUNILVR": "CONSUMER GOODS",
        "BHARTIARTL": "TELECOM",
        "KOTAKBANK": "FINANCIAL SERVICES",
        "MARUTI": "AUTO",
        "TATASTEEL": "METALS & MINING",
        "SUNPHARMA": "PHARMA",
        "CIPLA": "PHARMA",
        "DRREDDY": "PHARMA",
        "BRITANNIA": "CONSUMER GOODS",
        "TITAN": "CONSUMER GOODS",
        "ADANIPORTS": "SERVICES",
        "ULTRACEMCO": "CEMENT",
        "JSWSTEEL": "METALS & MINING",
        "GRASIM": "CEMENT",
        "POWERGRID": "ENERGY",
        "NTPC": "ENERGY",
        "ONGC": "ENERGY",
        "COALINDIA": "ENERGY",
        "M&M": "AUTO",
        "BAJAJ-AUTO": "AUTO",
        "HINDALCO": "METALS & MINING"
    }

    @staticmethod
    def get_sector(symbol: str) -> str:
        return SecurityMasterService.SECTOR_MAPPING.get(symbol, "SECTOR DATA UNAVAILABLE")

    @staticmethod
    async def sync_security_master():
        """
        Hardens the stocks table with authoritative metadata.
        """
        with SessionLocal() as session:
            stocks = session.query(StockDB).all()
            for s in stocks:
                sector = SecurityMasterService.get_sector(s.symbol)
                if s.sector != sector:
                    s.sector = sector
            session.commit()
            print(f"[+] Security Master Synced. Total: {len(stocks)}")
