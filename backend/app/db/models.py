"""
================================================================================
TradeMindAI: Local Database ORM Models
================================================================================
Establishes non-destructive SQLAlchemy ORM models with extend_existing=True guards
and performance-optimized database indexes for sub-50ms local query execution.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, UniqueConstraint
import datetime
from backend.app.db.database import Base

class MarketData(Base):
    __tablename__ = "app_market_data"
    __table_args__ = (
        Index("idx_market_data_sym_time", "symbol", "timestamp"),
        UniqueConstraint("symbol", "timestamp", name="uq_sym_timestamp"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False, default=0.0)

class Watchlist(Base):
    __tablename__ = "app_watchlists"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

class TradingSignal(Base):
    __tablename__ = "app_trading_signals"
    __table_args__ = (
        Index("idx_signals_sym_created", "symbol", "created_at"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(String(20), nullable=False) # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    confidence = Column(Float, nullable=False) # 0.0 - 100.0
    sentiment_score = Column(Float, default=0.0)
    drivers_json = Column(Text) # JSON string of key drivers
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class NewsArticle(Base):
    __tablename__ = "app_news_articles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, default=datetime.datetime.utcnow)
    sentiment_score = Column(Float, default=0.0)

class SentimentLog(Base):
    __tablename__ = "app_sentiment_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    sentiment_label = Column(String(20), nullable=False) # BULLISH, BEARISH, NEUTRAL
    score = Column(Float, nullable=False)
    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
