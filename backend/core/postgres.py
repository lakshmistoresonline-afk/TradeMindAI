from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Date, Numeric, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from .config import settings

# Hybrid Logic: Fallback to SQLite for local development if PG URL missing
DATABASE_URL = settings.POSTGRES_URL

from sqlalchemy import create_engine
# SQLite needs special args for concurrent access in some cases
engine_args = {"connect_args": {"check_same_thread": False}} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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

class PriceDB(Base):
    __tablename__ = "historical_prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    date = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    open_interest = Column(BigInteger)
    source = Column(String)
    indicators = Column(String) # JSON string

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
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String)
    prediction = Column(String)
    confidence = Column(Float)
    metadata_json = Column(String) # JSON string

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
    id = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    rating = Column(String)
    direction = Column(String)
    conviction = Column(Float)
    entry_price = Column(Float)
    target_price = Column(Float)
    stop_loss_price = Column(Float)
    timeframe = Column(String)
    status = Column(String)

    # F&O Support (RC-5)
    asset_class = Column(String(20), default="EQUITY")
    underlying_symbol = Column(String(20))
    strike = Column(Float)
    option_type = Column(String(10))
    expiry = Column(DateTime)
    lot_size = Column(Integer)

    # Quantitative Intelligence (P0 Update)
    raw_probability = Column(Float)
    calibrated_probability = Column(Float)
    expected_value = Column(Float)
    regime = Column(String)
    regime_probability = Column(Float)
    risk_reward = Column(Float)
    risk_per_unit = Column(Float)
    reward_per_unit = Column(Float)
    data_quality_score = Column(Float)
    feature_snapshot_id = Column(String)
    provenance = Column(String) # JSON string

    validated_at = Column(DateTime)
    triggered_at = Column(DateTime)
    trigger_price = Column(Float)
    trigger_condition = Column(String)

    outcome_date = Column(DateTime)
    profit_pct = Column(Float)
    outcome_price = Column(Float)
    mfe = Column(Float)
    mae = Column(Float)
    model_version = Column(String)
    events = Column(String) # JSON string

class WorkspaceDB(Base):
    __tablename__ = "workspaces"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    name = Column(String)
    type = Column(String)
    layout_config = Column(String) # JSON string
    active_stocks = Column(String) # JSON string
    saved_indicators = Column(String) # JSON string
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class ResearchNoteDB(Base):
    __tablename__ = "research_notes"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    symbol = Column(String, index=True)
    content = Column(String)
    tags = Column(String) # JSON string
    attachments = Column(String) # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class TradeJournalDB(Base):
    __tablename__ = "trade_journal"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    symbol = Column(String, index=True)
    entry_price = Column(Float)
    exit_price = Column(Float)
    quantity = Column(Integer)
    entry_date = Column(DateTime)
    exit_date = Column(DateTime)
    pnl = Column(Float)
    ai_score_at_entry = Column(Float)
    feedback = Column(String)
    mistakes = Column(String) # JSON string
    lessons = Column(String) # JSON string

class BulkDealDB(Base):
    __tablename__ = "bulk_deals"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    date = Column(DateTime, index=True)
    client_name = Column(String)
    deal_type = Column(String) # BUY / SELL
    quantity = Column(BigInteger)
    price = Column(Float)
    value_cr = Column(Float)
    source = Column(String, default="NSE")

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

def init_db():
    Base.metadata.create_all(bind=engine)

def get_pg_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
