import datetime
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy import func
from backend.core.postgres import SessionLocal, ShadowSignalDB, StockDB
from backend.domain.models.data_platform import PortfolioHealth

class ShadowPortfolioEngine:
    """
    Step 4: Hardened Shadow Portfolio Engine.
    Tracks virtual capital, exposure, and performance for Strategy V2.2.
    """
    STARTING_CAPITAL = 1000000.0
    UNIT_ALLOCATION = 100000.0

    @staticmethod
    def calculate_shadow_state() -> Dict[str, Any]:
        with SessionLocal() as session:
            # 1. Realized P&L
            terminal = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.status.in_(['TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'EXPIRED'])
            ).all()

            realized_pnl = 0.0
            for t in terminal:
                # P&L in currency = (Net Return % / 100) * Capital Allocation
                alloc = t.capital_allocation or ShadowPortfolioEngine.UNIT_ALLOCATION
                pnl_pct = t.net_return or 0.0
                realized_pnl += (pnl_pct / 100.0) * alloc

            # 2. Active Exposure & Unrealized P&L
            active = session.query(ShadowSignalDB, StockDB.last_price, StockDB.sector).join(
                StockDB, ShadowSignalDB.symbol == StockDB.symbol, isouter=True
            ).filter(ShadowSignalDB.status == 'ACTIVE').all()

            allocated_capital = 0.0
            unrealized_pnl = 0.0
            sector_exposure = {}
            concurrent_signals = len(active)

            for s, lp, sector in active:
                alloc = s.capital_allocation or ShadowPortfolioEngine.UNIT_ALLOCATION
                allocated_capital += alloc

                # Current P&L
                current_price = lp or s.entry_price
                if current_price and s.entry_price:
                    pnl_pct = 0.0
                    if s.direction == "LONG":
                        pnl_pct = (current_price - s.entry_price) / s.entry_price * 100
                    else:
                        pnl_pct = (s.entry_price - current_price) / s.entry_price * 100

                    unrealized_pnl += (pnl_pct / 100.0) * alloc

                # Sector Tracking (Part 41)
                sec = sector or "Unknown"
                sector_exposure[sec] = sector_exposure.get(sec, 0.0) + alloc

            current_equity = ShadowPortfolioEngine.STARTING_CAPITAL + realized_pnl + unrealized_pnl

            return {
                "starting_capital": ShadowPortfolioEngine.STARTING_CAPITAL,
                "current_equity": round(current_equity, 2),
                "realized_pnl": round(realized_pnl, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "allocated_capital": round(allocated_capital, 2),
                "available_capital": round(ShadowPortfolioEngine.STARTING_CAPITAL + realized_pnl - allocated_capital, 2),
                "gross_exposure": round(allocated_capital, 2),
                "net_exposure": round(allocated_capital, 2), # Assuming LONG-only for now
                "active_count": concurrent_signals,
                "terminal_count": len(terminal),
                "sector_exposure": sector_exposure,
                "drawdown": 0.0 # Peak tracking needed for real DD
            }

    @staticmethod
    def analyze_health(user_id: str, stocks: List[Any]) -> PortfolioHealth:
        """
        Connects API to real shadow stats for SYSTEM_SHADOW.
        """
        if user_id == "SYSTEM_SHADOW":
            state = ShadowPortfolioEngine.calculate_shadow_state()
            return PortfolioHealth(
                user_id=user_id,
                health_score=85.0,
                diversification_score=70.0,
                risk_level="MEDIUM",
                sector_allocation={},
                expected_annual_return=15.0,
                max_drawdown=state["drawdown"],
                equity=state["current_equity"]
            )

        # Original dummy for real users
        return PortfolioHealth(
            user_id=user_id,
            health_score=75.0,
            diversification_score=60.0,
            risk_level="LOW",
            sector_allocation={"Technology": 40.0, "Finance": 30.0, "Energy": 30.0},
            expected_annual_return=12.5,
            max_drawdown=5.2
        )
