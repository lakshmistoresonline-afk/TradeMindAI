from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Stock(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None

    # Pricing & Performance
    last_price: Optional[float] = None
    change_pct: Optional[float] = None
    weekly_change: Optional[float] = None
    monthly_change: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    avg_volume: Optional[float] = None
    delivery_pct: Optional[float] = None
    beta: Optional[float] = None

    # Valuation & Fundamentals
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    eps: Optional[float] = None
    debt_to_equity: Optional[float] = None
    book_value: Optional[float] = None
    dividend_yield: Optional[float] = None
    face_value: Optional[float] = None

    # Shareholding
    promoter_holding: Optional[float] = None
    fii_holding: Optional[float] = None
    dii_holding: Optional[float] = None
    public_holding: Optional[float] = None

    analysis: Optional[Dict[str, Any]] = None
    structured_consensus: Optional[Dict[str, Any]] = None
    ai_investment_score: Optional[float] = None
    ai_investment_grade: Optional[str] = None # AAA, AA, A, B, C, D
    health_metrics: Optional[Dict[str, str]] = None # "Financial": "GOOD", etc.
    confidence_metrics: Optional[Dict[str, Any]] = None
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
    indicators: Optional[Dict[str, Any]] = None
    smc: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return self.model_dump()
