from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Date, Numeric, BigInteger, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from .config import settings

# --- DATABASE URL RESOLUTION ---
# 1. Try environment variables
DATABASE_URL = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

# 2. Check for Production/Railway environment
is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
is_production = is_railway or os.getenv("ENVIRONMENT") == "production"

if not DATABASE_URL or "sqlite" in DATABASE_URL.lower():
    if not is_production:
        # Development Fallback (SQLite)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_path = os.path.join(base_dir, "backend", "local_operational.db")
        DATABASE_URL = f"sqlite:///{db_path}"
    else:
        # Production with no URL is an error
        print("[!] CRITICAL: Production mode detected but NO POSTGRES_URL provided.")

from sqlalchemy import create_engine
engine_args = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "connect_args": {"connect_timeout": 10}
}
if "sqlite" in DATABASE_URL:
    engine_args = {"connect_args": {"check_same_thread": False}}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Schema Definitions ---
class StockDB(Base):
    __tablename__ = "stocks"
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    last_price = Column(Float)
    change_pct = Column(Float)
    weekly_change = Column(Float)
    monthly_change = Column(Float)
    high_52w = Column(Float)
    low_52w = Column(Float)
    avg_volume = Column(Float)
    delivery_pct = Column(Float)
    beta = Column(Float)
    market_cap = Column(BigInteger)
    enterprise_value = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    peg_ratio = Column(Float)
    roe = Column(Float)
    roce = Column(Float)
    eps = Column(Float)
    debt_to_equity = Column(Float)
    book_value = Column(Float)
    dividend_yield = Column(Float)
    face_value = Column(Float)
    promoter_holding = Column(Float)
    fii_holding = Column(Float)
    dii_holding = Column(Float)
    public_holding = Column(Float)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    ai_investment_score = Column(Float)
    ai_investment_grade = Column(String)
    ai_status = Column(String, default="PENDING")
    ai_last_error = Column(String)
    analysis = Column(String) # JSON string
    structured_consensus = Column(String)
    options_data = Column(String)
    financial_history = Column(String)
    health_metrics = Column(String)
    confidence_metrics = Column(String)
    delivery_rate = Column(Float, default=0.0)
    options_pcr = Column(Float, default=1.0)
    sector_alpha = Column(Float, default=0.0)
    is_fno = Column(Boolean, default=False)
    lot_size = Column(Integer)
    index_weight = Column(Float)
    index_membership = Column(String) # NIFTY_50, NIFTY_100, NIFTY_200, INDEX
    universe_version = Column(String, default="NIFTY_200_AUG2026")
    data_freshness_status = Column(String) # FRESH, STALE, UNAVAILABLE
    missing_data_reason = Column(String)
    ingestion_timestamp = Column(DateTime)

class PriceDB(Base):
    __tablename__ = "historical_prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    open_interest = Column(BigInteger)
    source = Column(String)
    indicators = Column(JSON) # Changed from String to JSON for Postgres compatibility

class FeatureDefinitionDB(Base):
    __tablename__ = "feature_definitions"
    name = Column(String, primary_key=True)
    description = Column(String)
    category = Column(String)
    data_type = Column(String)
    min_value = Column(Float)
    max_value = Column(Float)
    version = Column(String)
    dependencies = Column(String)
    lineage = Column(String)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class RegimeDB(Base):
    __tablename__ = "market_regimes"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    regime = Column(String)
    risk_mode = Column(String)
    sentiment_score = Column(Float, default=0.5)
    description = Column(String)
    volatility_index = Column(Float)

class PredictionDB(Base):
    __tablename__ = "predictions"
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String)
    feature_version = Column(String)
    prediction = Column(String)
    probability = Column(Float)
    expected_value = Column(Float)
    direction = Column(String)
    confidence = Column(Float)
    regime = Column(String)
    metadata_json = Column(String) # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class IntelReportDB(Base):
    __tablename__ = "intel_reports"
    id = Column(String, primary_key=True)
    type = Column(String)
    date = Column(DateTime)
    summary = Column(String)
    key_events = Column(String) # JSON string
    ai_bias = Column(String)

class NewsDB(Base):
    __tablename__ = "news"
    id = Column(String, primary_key=True)
    symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    title = Column(String)
    url = Column(String)
    source = Column(String)
    published_at = Column(DateTime, index=True)
    content = Column(String)
    sentiment_label = Column(String)
    sentiment_score = Column(Float)

class EarningsDB(Base):
    __tablename__ = "earnings"
    id = Column(String, primary_key=True)
    symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    date = Column(DateTime, index=True)
    eps_actual = Column(Float)
    eps_estimate = Column(Float)
    revenue_actual = Column(Float)
    revenue_estimate = Column(Float)
    surprise_pct = Column(Float)

class OptionsChainDB(Base):
    __tablename__ = "options_chains"
    id = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    expiry = Column(DateTime, index=True)
    underlying_price = Column(Float)
    pcr = Column(Float)
    max_pain = Column(Float)
    total_oi = Column(BigInteger)
    iv_atm = Column(Float)
    greeks_aggregate = Column(String) # JSON string
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class MLDatasetDB(Base):
    __tablename__ = "ml_datasets"
    id = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    version = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    split_ratio = Column(Float)
    features_included = Column(String) # JSON string
    storage_path = Column(String)

class OpportunityDB(Base):
    __tablename__ = "opportunities"
    id = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    type = Column(String)
    conviction_score = Column(Float)
    ai_thesis = Column(String)
    indicators = Column(String) # JSON string
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class LiveSignalDB(Base):
    __tablename__ = "live_signals"
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    company_name = Column(String)
    exchange = Column(String, default="NSE")
    isin = Column(String)
    asset_type = Column(String) # EQUITY, DERIVATIVE
    instrument_id = Column(String)
    instrument_type = Column(String)
    direction = Column(String) # LONG, SHORT
    timeframe = Column(String)
    strategy_version = Column(String, default="v2.2")
    signal_version = Column(String, default="1.0")

    # Timing
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    signal_timestamp = Column(DateTime)
    decision_timestamp = Column(DateTime)
    data_timestamp = Column(DateTime)
    feature_timestamp = Column(DateTime)
    prediction_timestamp = Column(DateTime)
    price_timestamp = Column(DateTime)
    timezone = Column(String, default="UTC")
    timestamp = Column(DateTime) # Legacy alias

    # Trade Plan
    entry_price = Column(Float)
    entry_zone_low = Column(Float)
    entry_zone_high = Column(Float)
    target_price = Column(Float)
    stop_price = Column(Float)
    current_price = Column(Float)
    risk_reward_ratio = Column(Float)

    # Intelligence
    raw_probability = Column(Float)
    calibrated_probability = Column(Float)
    expected_value = Column(Float)
    opportunity_score = Column(Float)
    confidence = Column(Float)
    signal_score = Column(Float)

    regime = Column(String)
    regime_probability = Column(Float)
    risk_reward = Column(Float) # Legacy
    risk_per_unit = Column(Float)
    reward_per_unit = Column(Float)
    risk_amount_abs = Column(Float)
    reward_amount_abs = Column(Float)

    # Lineage
    model_id = Column(String)
    model_version = Column(String)
    model_hash = Column(String)
    model_run_id = Column(String)

    feature_snapshot_id = Column(String)
    feature_version = Column(String)
    feature_hash = Column(String)

    prediction_id = Column(String, index=True)
    provenance_id = Column(String, index=True)
    provenance = Column(String) # JSON string
    data_source = Column(String)
    data_source_timestamp = Column(DateTime)
    dataset_id = Column(String)
    dataset_hash = Column(String)

    # Lifecycle
    status = Column(String) # WAITING_FOR_ENTRY, ACTIVE, etc.
    lifecycle_state = Column(String)
    activated_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    exit_at = Column(DateTime)
    outcome_timestamp = Column(DateTime)

    # Outcome
    outcome = Column(String) # TARGET_HIT, STOP_LOSS, etc.
    exit_price = Column(Float)
    exit_reason = Column(String)
    realized_return = Column(Float)
    gross_pnl = Column(Float)
    transaction_cost = Column(Float)
    slippage = Column(Float)
    net_pnl = Column(Float)
    quality_class = Column(String) # PRIMARY, SELECTIVE, EXPERIMENTAL
    realized_mae = Column(Float)
    realized_mfe = Column(Float)
    holding_period_days = Column(Float)
    profit_pct = Column(Float) # Legacy alias

    # Quality
    price_status = Column(String) # Alias for current_price_status
    current_price_status = Column(String)
    current_price_source = Column(String)
    current_price_timestamp = Column(DateTime)
    data_quality_status = Column(String)
    validation_status = Column(String)
    audit_status = Column(String, default="PENDING")
    last_reconciled_at = Column(DateTime)
    record_hash = Column(String)
    data_quality_score = Column(Float)

    # Universal Price Tier
    underlying_price = Column(Float)
    price_source = Column(String)
    price_adjustment_factor = Column(Float, default=1.0)
    normalized_current_price = Column(Float)

    __table_args__ = (
        UniqueConstraint('symbol', 'strategy_version', 'direction', 'decision_timestamp', name='_symbol_strategy_direction_ts_uc'),
    )

    mfe = Column(Float) # Legacy
    mae = Column(Float) # Legacy
    events = Column(String) # JSON string

    # Step 3 Separation
    evaluation_mode = Column(String, default="LIVE_SHADOW")
    universe_version = Column(String, default="NIFTY_200_AUG2026")
    signal_eligibility = Column(String)
    outcome_verified = Column(Boolean, default=False)
    quantity = Column(Integer)
    capital_allocation = Column(Float)
    risk_amount = Column(Float)
    pnl_percentage = Column(Float)

    # F&O Support
    asset_class = Column(String(20), default="EQUITY")
    underlying_symbol = Column(String(20))
    strike = Column(Float)
    option_type = Column(String(10))
    expiry = Column(DateTime)
    lot_size = Column(Integer)
    rating = Column(String) # Legacy
    conviction = Column(Float) # Legacy
    validated_at = Column(DateTime)
    triggered_at = Column(DateTime)
    trigger_price = Column(Float)
    trigger_condition = Column(String)
    outcome_date = Column(DateTime)

class ShadowSignalDB(Base):
    __tablename__ = "shadow_signals"
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    symbol = Column(String, index=True)
    direction = Column(String)
    asset_class = Column(String(20), default="EQUITY")
    instrument_id = Column(String)
    instrument_type = Column(String)
    raw_probability = Column(Float)
    calibrated_probability = Column(Float)
    expected_value = Column(Float)
    data_quality_score = Column(Float)
    entry_price = Column(Float)
    target_price = Column(Float)
    stop_price = Column(Float)
    strategy_version = Column(String, default="v2.2")
    universe_version = Column(String, default="NIFTY_200_AUG2026")
    model_version = Column(String)
    feature_version = Column(String)
    regime = Column(String)
    outcome = Column(String) # For legacy compatibility, redundant with status
    outcome_timestamp = Column(DateTime)
    exit_price = Column(Float)
    realized_return = Column(Float)
    realized_mfe = Column(Float)
    realized_mae = Column(Float)
    transaction_cost = Column(Float) # Fees
    slippage = Column(Float)
    net_return = Column(Float)
    exit_reason = Column(String)
    data_timestamp = Column(DateTime)
    market_timestamp = Column(DateTime)
    evaluation_mode = Column(String, default="LIVE_SHADOW", index=True)
    status = Column(String, default="ACTIVE", index=True)
    signal_eligibility = Column(String)
    outcome_verified = Column(Boolean, default=False)
    quantity = Column(Integer)
    capital_allocation = Column(Float)
    risk_amount = Column(Float)
    gross_pnl = Column(Float)
    pnl_percentage = Column(Float)
    fees = Column(Float)
    net_pnl = Column(Float)
    quality_class = Column(String) # PRIMARY, SELECTIVE, EXPERIMENTAL
    prediction_id = Column(String, index=True)
    provenance_id = Column(String, index=True)
    run_id = Column(String, index=True)
    dataset_type = Column(String, index=True) # V2.2_VERIFIED_REFERENCE, V2.2_HISTORICAL_REPLAY, V2.2_CURRENT_SHADOW
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Ledger 2.0 Extensions
    asset_type = Column(String(20)) # EQUITY, DERIVATIVE
    exchange = Column(String(10), default="NSE")
    underlying_symbol = Column(String(20))
    signal_type = Column(String(20)) # SWING, INTRADAY
    signal_rating = Column(String(10)) # BUY, SELL
    conviction = Column(Float)
    entry_zone_low = Column(Float)
    entry_zone_high = Column(Float)
    current_price = Column(Float)
    underlying_price = Column(Float)
    underlying_price_timestamp = Column(DateTime)
    price_adjustment_factor = Column(Float, default=1.0)
    price_timestamp = Column(DateTime)
    price_source = Column(String)
    price_status = Column(String)

    # Derivative extensions
    derivative_symbol = Column(String(50))
    contract_multiplier = Column(Integer)
    strike = Column(Float)
    expiry = Column(DateTime)
    option_type = Column(String(10))
    derivative_entry = Column(Float)
    derivative_current = Column(Float)
    derivative_target = Column(Float)
    derivative_stop = Column(Float)
    premium_timestamp = Column(DateTime)

    # Timing Extensions
    signal_timestamp = Column(DateTime)
    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    entry_timestamp = Column(DateTime)
    exit_timestamp = Column(DateTime)

    # Lifecycle Extensions
    lifecycle_state = Column(String(30)) # CREATED, ENTERED, TERMINAL
    outcome_status = Column(String(30))
    verification_level = Column(Integer, default=0)

    # Risk/Reward Extensions
    risk_amount_abs = Column(Float)
    reward_amount_abs = Column(Float)
    risk_reward_ratio = Column(Float)
    expected_return = Column(Float)

    # Traceability Extensions
    feature_snapshot_id = Column(String)
    market_snapshot_id = Column(String)
    model_run_id = Column(String)
    decision_id = Column(String)

    # Audit Extensions
    created_by = Column(String, default="SYSTEM")
    calculation_version = Column(String, default="1.0")
    pnl_engine_version = Column(String, default="1.0")
    outcome_engine_version = Column(String, default="1.0")
    reconstruction_version = Column(String, default="1.0")
    last_reconciled_at = Column(DateTime)
    record_hash = Column(String)
    audit_status = Column(String, default="PENDING")

class SignalCorrectionDB(Base):
    __tablename__ = "signal_corrections"
    id = Column(Integer, primary_key=True)
    signal_id = Column(String, ForeignKey("shadow_signals.id"), index=True)
    field_name = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    reason = Column(String)
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)
    detected_by = Column(String)
    approved_by = Column(String)
    correction_version = Column(String)
    evidence_reference = Column(String)

class ShadowProvenanceDB(Base):
    __tablename__ = "shadow_provenance"
    id = Column(String, primary_key=True)
    signal_id = Column(String, index=True)
    prediction_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    data_snapshot_timestamp = Column(DateTime)
    model_version = Column(String)
    strategy_version = Column(String)
    feature_version = Column(String)
    data_sources = Column(String) # JSON
    source_timestamps = Column(String) # JSON
    input_hash = Column(String)
    output_hash = Column(String)
    decision_hash = Column(String)

class ShadowEventDB(Base):
    __tablename__ = "shadow_events"
    id = Column(Integer, primary_key=True)
    signal_id = Column(String, index=True) # Optional link to a specific signal
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String, index=True) # EVALUATION, OUTCOME_RESOLUTION, GATE_FAILURE
    symbol = Column(String, index=True)
    strategy_version = Column(String)
    model_version = Column(String)
    decision = Column(String) # TRADE_SIGNAL, NO_TRADE, etc.
    rejection_reason = Column(String)
    payload_json = Column(String) # For detailed parameters (EMA, ATR, Prob, etc.)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    evaluation_mode = Column(String, default="LIVE_SHADOW", index=True)

class ShadowScanDiagnosticDB(Base):
    __tablename__ = "shadow_scan_diagnostics"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    scan_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    market_data_timestamp = Column(DateTime)
    data_age_hours = Column(Float)
    signal_score = Column(Float)
    threshold = Column(Float, default=0.52)
    liquidity_status = Column(String) # PASS, FAIL
    stale_data_status = Column(String) # FRESH, STALE, MARKET_CLOSED
    signal_decision = Column(String) # SIGNAL_GENERATED, REJECTED
    rejection_reason = Column(String)
    model_version = Column(String)
    provider_name = Column(String)
    provider_latency_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SectorMetricDB(Base):
    __tablename__ = "sector_metrics"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    sector = Column(String, index=True)
    relative_strength = Column(Float)
    momentum = Column(Float)
    trend = Column(String) # BULLISH, BEARISH, SIDEWAYS
    volume_score = Column(Float)
    volatility = Column(Float)
    rank = Column(Integer)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class InstitutionalMetricDB(Base):
    __tablename__ = "institutional_metrics"
    date = Column(Date, primary_key=True)
    fii_net = Column(Float)
    dii_net = Column(Float)
    fii_cumulative = Column(Float)
    dii_cumulative = Column(Float)
    sentiment_bias = Column(String) # BULLISH, BEARISH, NEUTRAL
    institutional_pressure = Column(Float) # -1.0 to 1.0
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class StockIntelligenceDB(Base):
    __tablename__ = "stock_intelligence"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    date = Column(Date, index=True)
    trend_score = Column(Float)
    momentum_score = Column(Float)
    volatility_score = Column(Float)
    volume_score = Column(Float)
    rs_rating = Column(Float)
    technical_structure = Column(String) # JSON
    fundamental_score = Column(Float)
    institutional_pressure = Column(Float)
    market_regime = Column(String)
    sector_regime = Column(String)
    composite_intelligence_score = Column(Float)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class IntelligenceSynthesisDB(Base):
    __tablename__ = "intelligence_synthesis"
    id = Column(String, primary_key=True) # Usually signal_id or prediction_id
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    market_context = Column(String) # JSON
    sector_context = Column(String) # JSON
    technical_context = Column(String) # JSON
    fundamental_context = Column(String) # JSON
    institutional_context = Column(String) # JSON
    fo_context = Column(String) # JSON
    supporting_evidence = Column(String) # JSON
    conflicting_evidence = Column(String) # JSON
    risk_factors = Column(String) # JSON
    final_interpretation = Column(String)

class DailyMetricDB(Base):
    __tablename__ = "daily_metrics"
    date = Column(Date, primary_key=True)
    universe_version = Column(String)
    signals_generated = Column(Integer)
    signals_active = Column(Integer)
    target_hits = Column(Integer)
    stop_losses = Column(Integer)
    timeouts = Column(Integer)
    expired = Column(Integer)
    cancelled = Column(Integer)
    invalid_outcomes = Column(Integer)
    gross_pnl = Column(Float)
    fees = Column(Float)
    slippage = Column(Float)
    net_pnl = Column(Float)
    virtual_equity = Column(Float)
    drawdown = Column(Float)
    exposure = Column(Float)
    provider_reliability_pct = Column(Float)
    avg_latency_ms = Column(Integer)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class ModelMetadataDB(Base):
    __tablename__ = "model_registry"
    name = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    version = Column(String)
    horizon = Column(String, index=True, default="SWING") # Phase 11 Extension
    type = Column(String)
    status = Column(String, default="CANDIDATE")
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    brier_score = Column(Float)
    is_champion = Column(Boolean, default=False)
    last_trained = Column(DateTime, default=datetime.datetime.utcnow)
    hyperparameters = Column(String) # JSON string
    feature_importances = Column(String) # JSON string
    calibration_metadata = Column(String) # JSON string

class InstrumentDB(Base):
    __tablename__ = "instruments"
    id = Column(String, primary_key=True)
    exchange = Column(String)
    trading_symbol = Column(String)
    segment = Column(String)
    instrument_type = Column(String)
    groww_symbol = Column(String, index=True)
    underlying_symbol = Column(String)
    expiry = Column(DateTime)
    strike = Column(Float)
    option_type = Column(String)
    lot_size = Column(Integer)
    tick_size = Column(Float)
    source = Column(String)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class UserWatchlistDB(Base):
    __tablename__ = "user_watchlists"
    user_id = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserSubscriptionDB(Base):
    __tablename__ = "user_subscriptions"
    user_id = Column(String, primary_key=True)
    plan_id = Column(String) # FREE, PRO, ALPHA
    status = Column(String) # ACTIVE, CANCELLED, EXPIRED
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    provider_subscription_id = Column(String)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserReferralDB(Base):
    __tablename__ = "user_referrals"
    id = Column(String, primary_key=True)
    referrer_id = Column(String, index=True)
    referred_email = Column(String, unique=True)
    status = Column(String) # SENT, REGISTERED, CONVERTED
    reward_earned = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

from sqlalchemy import event
from .config import settings

@event.listens_for(LiveSignalDB, 'before_insert')
def guard_live_signal(mapper, connection, target):
    # Part 4/34: Environment Guard
    if settings.ENVIRONMENT in ["production", "shadow"] and target.evaluation_mode == "TEST":
        raise ValueError(f"CRITICAL: Rejected TEST signal insertion into {settings.ENVIRONMENT} database.")

@event.listens_for(ShadowSignalDB, 'before_insert')
def guard_shadow_signal(mapper, connection, target):
    if settings.ENVIRONMENT in ["production", "shadow"] and target.evaluation_mode == "TEST":
        raise ValueError(f"CRITICAL: Rejected TEST signal insertion into {settings.ENVIRONMENT} database.")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_pg_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
