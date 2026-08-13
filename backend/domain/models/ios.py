from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class WorkspaceState(BaseModel):
    id: str
    user_id: str
    name: str
    type: str # INTRADAY, SWING, LONG_TERM, etc.
    layout_config: Dict[str, Any]
    active_stocks: List[str]
    saved_indicators: List[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchNote(BaseModel):
    id: str
    user_id: str
    symbol: str
    content: str
    tags: List[str] = []
    attachments: List[str] = [] # URLs to Firebase Storage
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MarketRegime(BaseModel):
    date: datetime
    regime: str # BULL, BEAR, SIDEWAYS, VOLATILE
    risk_mode: str # RISK_ON, RISK_OFF
    sentiment_score: float
    volatility_index: float
    description: str

class MarketOpportunity(BaseModel):
    id: str
    symbol: str
    type: str # BREAKOUT, REVERSAL, MOMENTUM, UNDERVALUED
    conviction_score: float
    ai_thesis: str
    indicators: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SignalEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str # GENERATED, VALIDATED, ENTRY_TRIGGERED, POSITION_ACTIVE, TARGET_HIT, STOP_LOSS, EXPIRED, CANCELLED
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    price: Optional[float] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class LiveSignal(BaseModel):
    id: str
    symbol: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    rating: str
    direction: str # LONG or SHORT
    conviction: float
    entry_price: float
    target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    timeframe: str
    status: str # WAITING_FOR_ENTRY, ENTRY_TRIGGERED, ACTIVE, TARGET_HIT, STOP_LOSS, EXPIRED, CANCELLED

    validated_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    trigger_price: Optional[float] = None
    trigger_condition: Optional[str] = None

    outcome_date: Optional[datetime] = None
    profit_pct: Optional[float] = None
    mfe: float = 0.0
    mae: float = 0.0
    model_version: str = "TradeMind Core v2.2"
    events: List[SignalEvent] = []

class TradeFeedback(BaseModel):
    id: str
    user_id: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    entry_date: datetime
    exit_date: datetime
    pnl: float
    ai_score_at_entry: float
    feedback: str # AI generated feedback
    mistakes: List[str]
    lessons: List[str]

class MarketIntelligenceReport(BaseModel):
    id: str
    type: str # MORNING, CLOSING, WEEKLY
    date: datetime
    summary: str
    key_events: List[str]
    top_movers: List[Dict[str, Any]]
    sector_performance: Dict[str, float]
    ai_bias: str
