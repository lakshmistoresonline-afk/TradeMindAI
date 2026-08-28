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

    # F&O Support (RC-5)
    asset_class: str = "EQUITY" # EQUITY, FUTURES, OPTIONS
    underlying_symbol: Optional[str] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None # CE or PE
    expiry: Optional[datetime] = None
    lot_size: Optional[int] = None

    # Canonical Identity (Step 2C Upgrade)
    instrument_id: Optional[str] = None
    instrument_type: Optional[str] = None

    # Quantitative Intelligence (P0 Update)
    raw_probability: Optional[float] = None
    calibrated_probability: Optional[float] = None
    expected_value: Optional[float] = None
    regime: Optional[str] = None
    regime_probability: Optional[float] = None
    risk_reward: Optional[float] = None
    risk_per_unit: Optional[float] = None
    reward_per_unit: Optional[float] = None
    data_quality_score: Optional[float] = None
    feature_snapshot_id: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)

    validated_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    trigger_price: Optional[float] = None
    trigger_condition: Optional[str] = None

    outcome_date: Optional[datetime] = None
    profit_pct: Optional[float] = None
    outcome_price: Optional[float] = None

    # Universal Price Tier (Step 2C/D/E/F)
    current_price: Optional[float] = None
    underlying_price: Optional[float] = None
    current_price_timestamp: Optional[datetime] = None
    price_source: Optional[str] = None
    price_status: Optional[str] = None # FRESH, STALE, MARKET_CLOSED, DATA_UNAVAILABLE, PROVIDER_UNSUPPORTED, INSTRUMENT_NOT_FOUND, INVALID
    price_adjustment_factor: float = 1.0
    normalized_current_price: Optional[float] = None
    signal_eligibility: Optional[str] = None # ELIGIBLE, DATA_BLOCKED, INSTRUMENT_BLOCKED, STALE_DATA, EXPIRED_INSTRUMENT, INVALID_DATA
    evaluation_mode: str = "LIVE_SHADOW" # LIVE_SHADOW, HISTORICAL, BACKTEST, TEST
    universe_version: str = "NIFTY_200_AUG2026"
    strategy_version: str = "v2.2"
    data_timestamp: Optional[datetime] = None
    market_timestamp: Optional[datetime] = None
    exit_reason: Optional[str] = None
    fees: Optional[float] = None
    slippage: Optional[float] = None
    net_pnl: Optional[float] = None
    outcome_verified: bool = False
    quantity: Optional[int] = None
    capital_allocation: Optional[float] = None
    risk_amount: Optional[float] = None
    gross_pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None

    # Forensic Execution Fields (Step 4 Corrective)
    actual_entry_price: Optional[float] = None
    entry_execution_type: Optional[str] = None # NORMAL, FAVORABLE_GAP, INTRABAR
    bars_to_entry: int = 0
    bars_in_position: int = 0
    bars_to_expiry: int = 0

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
