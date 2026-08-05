from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Stock(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None
    last_price: Optional[float] = None
    change_pct: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return self.model_dump()

class StockPrice(BaseModel):
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    def to_dict(self):
        return self.model_dump()
