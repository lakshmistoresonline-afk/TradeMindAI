from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Date, Numeric, BigInteger, JSON
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
    analysis = Column(JSON) # Consensus Agent results
    structured_consensus = Column(JSON)
    health_metrics = Column(JSON)
    confidence_metrics = Column(JSON)

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
    indicators = Column(JSON) # EMA, RSI, MACD, etc.

class FeatureDefinitionDB(Base):
    __tablename__ = "feature_definitions"
    name = Column(String, primary_key=True)
    description = Column(String)
    category = Column(String)
    data_type = Column(String)
    min_value = Column(Float)
    max_value = Column(Float)
    version = Column(String)
    dependencies = Column(JSON)
    lineage = Column(JSON)
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
    metadata_json = Column(JSON) # renmaed to avoid collision with pydantic

class IntelReportDB(Base):
    __tablename__ = "intel_reports"
    id = Column(String, primary_key=True)
    type = Column(String)
    date = Column(DateTime)
    summary = Column(String)
    key_events = Column(JSON)
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
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_pg_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
