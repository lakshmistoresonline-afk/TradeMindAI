from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NewsArticle(BaseModel):
    id: str
    symbol: str
    title: str
    url: str
    source: str
    published_at: datetime
    content: str
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"

class InstitutionalFlow(BaseModel):
    date: datetime
    fii_net: float # In Crores
    dii_net: float
    market_sentiment: str

class CorporateAction(BaseModel):
    symbol: str
    date: datetime
    type: str # DIVIDEND, SPLIT, BONUS
    value: float
    ratio: Optional[str] = None

class MacroIndicator(BaseModel):
    name: str # GDP, INFLATION, INTEREST_RATE
    value: float
    date: datetime
    unit: str

class FeatureDefinition(BaseModel):
    name: str
    description: str
    category: str # TECHNICAL, FUNDAMENTAL, MACRO, SMC, ICT, WYCKOFF, ELLIOTT, OPTIONS
    data_type: str # FLOAT, INT, BOOLEAN
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    version: str
    dependencies: List[str] = []
    lineage: Dict[str, str] = {} # Map of source data to transformation
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class EarningsData(BaseModel):
    symbol: str
    date: datetime
    eps_actual: float
    eps_estimate: Optional[float] = None
    revenue_actual: float
    revenue_estimate: Optional[float] = None
    surprise_pct: Optional[float] = None

class OptionsChain(BaseModel):
    symbol: str
    expiry: datetime
    underlying_price: float
    pcr: float
    max_pain: float
    total_oi: int
    iv_atm: float
    greeks_aggregate: Dict[str, float]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class FeatureVector(BaseModel):
    symbol: str
    date: datetime
    version: str
    features: Dict[str, float]
    target: Optional[float] = None # For ML Training
    metadata: Dict[str, Any] = {}

class Prediction(BaseModel):
    symbol: str
    date: datetime
    model_version: str
    prediction: str # UP, DOWN, NEUTRAL
    confidence: float
    metadata: Dict[str, Any]

class MLDataset(BaseModel):
    id: str
    symbol: str
    version: str
    created_at: datetime
    start_date: datetime
    end_date: datetime
    split_ratio: float # e.g. 0.8 for train/test
    features_included: List[str]
    storage_path: Optional[str] = None # For cloud storage paths if large

class ModelMetadata(BaseModel):
    name: str
    symbol: str
    version: str
    type: str # RANDOM_FOREST, LSTM, XGBOOST
    accuracy: float
    precision: float
    recall: float
    is_champion: bool = False
    last_trained: datetime
    hyperparameters: Dict[str, Any]
    feature_importances: Dict[str, float] = {}

class OptionsMetric(BaseModel):
    symbol: str
    date: datetime
    pcr: float
    max_pain: float
    total_oi: int
    iv_rank: float
    iv_percentile: float

class QuantMetric(BaseModel):
    symbol: str
    date: datetime
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    volatility: float

class PortfolioHealth(BaseModel):
    user_id: str
    health_score: float # 0-100
    diversification_score: float
    risk_level: str # LOW, MED, HIGH
    sector_allocation: Dict[str, float]
    expected_annual_return: float
    max_drawdown: float
    avg_beta: float = 1.0
    asset_correlation: float = 0.5
    var_95: float = 0.0 # Value at Risk

class Alert(BaseModel):
    id: str
    symbol: str
    type: str # SMC_BREAK, HIGH_CONFIDENCE_BUY, VOLATILITY_SPIKE
    message: str
    severity: str # INFO, WARNING, CRITICAL
    created_at: datetime
    is_read: bool = False
