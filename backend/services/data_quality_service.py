import datetime
from typing import Dict, Any, List
from backend.domain.models.stock import StockPrice

class DataQualityService:
    """
    Workstream 11: Production Data Quality & Validation Layer.
    """
    @staticmethod
    def validate_candle_data(prices: List[StockPrice]) -> Dict[str, Any]:
        now = datetime.datetime.utcnow()
        issues = []

        for p in prices:
            # 1. Future check
            if p.date > now + datetime.timedelta(minutes=5):
                issues.append(f"FUTURE_TIMESTAMP: {p.symbol} @ {p.date}")

            # 2. OHLC Logic
            if p.low > p.high or p.low > p.open or p.low > p.close:
                issues.append(f"INVALID_LOW: {p.symbol} @ {p.date}")
            if p.high < p.open or p.high < p.close:
                issues.append(f"INVALID_HIGH: {p.symbol} @ {p.date}")

        return {
            "status": "PASS" if not issues else "FAIL",
            "issue_count": len(issues),
            "details": issues[:10] # Cap reporting
        }

    @staticmethod
    def check_price_freshness(updated_at: datetime) -> str:
        if not updated_at: return "UNAVAILABLE"
        age = (datetime.datetime.utcnow() - updated_at).total_seconds() / 60.0 # mins
        if age < 5: return "FRESH"
        if age < 60: return "DELAYED"
        return "STALE"

    @staticmethod
    def audit_signal_geometry(entry: float, target: float, stop: float, direction: str) -> bool:
        """
        Ensures signal parameters are logically sound before generation.
        """
        if direction == "LONG":
            return target > entry and stop < entry
        else:
            return target < entry and stop > entry
