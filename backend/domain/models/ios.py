from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

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
    type: str
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
    company_name: Optional[str] = None
    exchange: str = "NSE"
    isin: Optional[str] = None
    asset_type: Optional[str] = None # EQUITY, DERIVATIVE
    instrument_id: Optional[str] = None
    instrument_type: Optional[str] = None
    direction: str # LONG or SHORT
    rating: Optional[str] = None # BUY, SELL, HOLD
    timeframe: Optional[str] = None
    strategy_version: str = "v2.5"
    signal_version: str = "1.0"

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    signal_timestamp: Optional[datetime] = None
    decision_timestamp: Optional[datetime] = None
    data_timestamp: Optional[datetime] = None
    feature_timestamp: Optional[datetime] = None
    prediction_timestamp: Optional[datetime] = None
    price_timestamp: Optional[datetime] = None
    timezone: str = "UTC"
    timestamp: Optional[datetime] = None # Legacy alias

    # Price & 3-Target Profit Geometry
    entry_price: Optional[float] = None
    entry_zone_low: Optional[float] = None
    entry_zone_high: Optional[float] = None
    target_price: Optional[float] = None     # Legacy/Default Target
    target_price_1: Optional[float] = None   # Target 1 (Conservative 1.5x ATR)
    target_price_2: Optional[float] = None   # Target 2 (Base Structural 2.8x ATR)
    target_price_3: Optional[float] = None   # Target 3 (Extended Runner 4.2x ATR)
    stop_price: Optional[float] = None
    current_price: Optional[float] = None
    risk_reward_ratio: Optional[float] = None

    # Intelligence & Strategy V2.5 Accuracy Upgrades
    raw_probability: Optional[float] = None
    calibrated_probability: Optional[float] = None
    expected_value: Optional[float] = None
    opportunity_score: Optional[float] = None
    confidence: Optional[float] = None
    signal_score: Optional[float] = None

    # V2.5 Accuracy Features
    net_dealer_gex: Optional[float] = None          # Options Surface Gamma Exposure
    sector_rrg_quadrant: Optional[str] = None      # LEADING, IMPROVING, WEAKENING, LAGGING
    conformal_coverage_pct: Optional[float] = None # Certified Conformal Coverage (e.g. 92.5%)
    order_book_imbalance: Optional[float] = None   # Top 5 BBO Bid/Ask Imbalance Ratio
    shap_drivers: Dict[str, float] = Field(default_factory=dict) # SHAP Feature Weighting

    regime: Optional[str] = None
    regime_probability: Optional[float] = None

    # Lineage
    model_id: Optional[str] = None
    model_version: str = "TradeMind Core v2.5-Ensemble"
    model_hash: Optional[str] = None
    model_run_id: Optional[str] = None

    feature_snapshot_id: Optional[str] = None
    feature_version: Optional[str] = None
    feature_hash: Optional[str] = None

    prediction_id: Optional[str] = None
    provenance_id: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    data_source: Optional[str] = None
    data_source_timestamp: Optional[datetime] = None
    dataset_id: Optional[str] = None
    dataset_hash: Optional[str] = None

    # Lifecycle
    status: str # WAITING_FOR_ENTRY, ACTIVE, etc.
    lifecycle_state: Optional[str] = None
    activated_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    exit_at: Optional[datetime] = None
    outcome_timestamp: Optional[datetime] = None

    # Outcome
    outcome: Optional[str] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    holding_period_days: Optional[float] = None
    realized_return: Optional[float] = None
    gross_pnl: Optional[float] = None
    transaction_cost: Optional[float] = None
    slippage: Optional[float] = None
    net_pnl: Optional[float] = None
    realized_mae: Optional[float] = None
    realized_mfe: Optional[float] = None

    # Quality
    quality_class: str = "PRIMARY" # PRIMARY, SELECTIVE, EXPERIMENTAL
    current_price_status: Optional[str] = None
    current_price_source: Optional[str] = None
    current_price_timestamp: Optional[datetime] = None
    data_quality_status: Optional[str] = None
    validation_status: Optional[str] = None
    audit_status: str = "PENDING"
    last_reconciled_at: Optional[datetime] = None
    record_hash: Optional[str] = None
    data_quality_score: Optional[float] = None
    deployment_sha: Optional[str] = None

    # Entry Instrumentation
    candidate_timestamp: Optional[datetime] = None
    published_at: Optional[datetime] = None
    price_at_signal: Optional[float] = None
    price_at_publish: Optional[float] = None
    price_at_activation: Optional[float] = None

    # Regime Instrumentation
    regime_timestamp: Optional[datetime] = None
    regime_source: Optional[str] = None
    regime_confidence: Optional[float] = None
    regime_available: bool = False

    # Legacy/Internal Compatibility
    rating: Optional[str] = None
    conviction: Optional[float] = None
    asset_class: str = "EQUITY"
    underlying_symbol: Optional[str] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None
    expiry: Optional[datetime] = None
    lot_size: Optional[int] = None
    quantity: Optional[int] = None
    capital_allocation: Optional[float] = None
    signal_eligibility: Optional[str] = None
    evaluation_mode: str = "LIVE_SHADOW"
    universe_version: str = "NIFTY_200_AUG2026"
    data_timestamp_legacy: Optional[datetime] = None
    market_timestamp: Optional[datetime] = None
    outcome_verified: bool = False
    events: List[SignalEvent] = []
    mfe: float = 0.0
    mae: float = 0.0
    profit_pct: Optional[float] = None

class MarketIntelligenceReport(BaseModel):
    id: str
    type: str
    date: datetime
    summary: str
    key_events: List[str]
    top_movers: List[Dict[str, Any]]
    sector_performance: Dict[str, float]
    ai_bias: str
