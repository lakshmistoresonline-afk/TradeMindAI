from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class StrategyBlock(BaseModel):
    id: str
    type: str # INDICATOR, OPERATOR, VALUE, ACTION
    name: str
    params: Dict[str, Any]

class UserStrategy(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    blocks: List[StrategyBlock]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class PaperOrder(BaseModel):
    id: str
    user_id: str
    strategy_id: Optional[str] = None
    symbol: str
    type: str # BUY, SELL
    price: float
    quantity: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str # OPEN, CLOSED, CANCELLED

class VirtualPortfolio(BaseModel):
    user_id: str
    cash_balance: float = 1000000.0 # Start with 10L INR
    holdings: Dict[str, int] = {} # Symbol -> Quantity
    pnl_history: List[Dict[str, Any]] = []
