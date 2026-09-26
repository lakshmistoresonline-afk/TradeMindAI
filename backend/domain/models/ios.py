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
    strategy_version: str = "v3.3"
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

    # Intelligence & Strategy V2.5-V3.3 Accuracy Upgrades
    raw_probability: Optional[float] = None
    calibrated_probability: Optional[float] = None
    expected_value: Optional[float] = None
    opportunity_score: Optional[float] = None
    confidence: Optional[float] = None
    signal_score: Optional[float] = None

    # V2.5 & V2.6 Accuracy Features
    net_dealer_gex: Optional[float] = None          # Options Surface Gamma Exposure
    sector_rrg_quadrant: Optional[str] = None      # LEADING, IMPROVING, WEAKENING, LAGGING
    conformal_coverage_pct: Optional[float] = None # Certified Conformal Coverage (e.g. 92.5%)
    order_book_imbalance: Optional[float] = None   # Top 5 BBO Bid/Ask Imbalance Ratio
    shap_drivers: Dict[str, float] = Field(default_factory=dict) # SHAP Feature Weighting

    # V2.6 Quantitative Upgrades
    hmm_regime_state: Optional[str] = None          # STEADY_BULL_TREND, MEAN_REVERSION_CHOP, VOLATILE_CORRECTION, LIQUIDATION_CRASH
    cvd_tape_pressure: Optional[float] = None       # Intraday Cumulative Volume Delta Tape Pressure (+0.48)
    max_pain_shift_vector: Optional[float] = None   # Options Max Pain Strike Displacement Velocity (+15.0)
    venn_abers_lower_prob: Optional[float] = None   # Venn-ABERS Lower-Bound Probability Certificate (0.72)
    beta_adjusted_targets: Dict[str, float] = Field(default_factory=dict) # Beta-Scaled Target Geometry

    # V2.7 Apex Quantitative Upgrades
    vpin_flow_toxicity: Optional[float] = None      # VPIN Volume-Synchronized Flow Toxicity (0.82)
    dark_pool_dix_index: Optional[float] = None      # Off-Exchange Dark Pool Accumulation Index (+0.68)
    finbert_nlp_sentiment: Optional[float] = None   # FinBERT Filings NLP Sentiment Score (+0.75)
    intermarket_cointegration_score: Optional[float] = None # Global Intermarket Alignment (+0.88)
    ppo_rl_exit_status: Optional[str] = None        # HOLD_DYNAMIC_TRAIL, MARKET_SELL, BREAKEVEN_LOCK

    # V2.8 Autonomous Swarm & Quantum Upgrades
    agent_swarm_consensus_score: Optional[float] = None   # 4-Agent LLM Committee Consensus Score (e.g. 0.95)
    quantum_density_probability: Optional[float] = None   # Schrödinger Wave Probability Density (e.g. 0.88)
    rmt_cluster_uncorrelated_score: Optional[float] = None# Random Matrix Theory Noise-Filtered Covariance Score (e.g. 0.92)
    tsallis_entropy_exhaustion_index: Optional[float] = None# Tsallis Non-Extensive Information Entropy Index (e.g. 0.18)
    lob_queue_impact_cost: Optional[float] = None          # LOB Queue Priority Impact Cost Estimator (e.g. 0.02%)

    # V2.9 Neuromorphic & Topological Upgrades
    snn_tape_spike_detected: Optional[bool] = None         # Neuromorphic Spiking Neural Net Sub-Millisecond Tape Spike (True)
    tda_betti_homology_score: Optional[float] = None       # Topological Data Analysis Persistent Homology Score (0.94)
    hurst_exponent_h: Optional[float] = None               # Fractional Brownian Motion Hurst Memory Exponent (0.72)
    zk_snark_proof_hash: Optional[str] = None              # Cryptographic Zero-Knowledge zk-SNARK Proof of Alpha Hash
    variance_swap_arbitrage_score: Optional[float] = None  # Implied Volatility vs OFI Variance Mispricing (+2.85 sigma)

    # V3.0 Quantum-Classical Hybrid & Causal Upgrades
    causal_do_calculus_score: Optional[float] = None        # Structural Causal Do-Calculus Causal Effect Score (0.98)
    vqe_quantum_portfolio_state: Optional[str] = None       # Variational Quantum Eigensolver QUBO State (EIGEN_STATE_OPTIMAL_QUBO)
    hawkes_intensity_spike: Optional[float] = None          # Self-Exciting Hawkes Process Order Arrival Intensity (4.2x)
    wgan_synthetic_survival_rate: Optional[float] = None    # WGAN-GP Synthetic Crash Stress Test Survival Rate (100.0%)
    alor_queue_priority_status: Optional[str] = None        # Atomic Limit Order Routing Queue Priority (NBBO_TOUCH_ZERO_SLIPPAGE)

    # V3.1 AGI Swarm Synthesis & Lyapunov Chaos Upgrades
    trademind_gpt_conviction_score: Optional[float] = None   # TradeMindGPT-7B Macro-Micro Fine-Tuned LLM Score (0.99)
    lyapunov_exponent_lambda1: Optional[float] = None        # Maximal Lyapunov Exponent Phase Gate (-0.05 Laminar Stability)
    clayton_copula_tail_contagion_risk: Optional[float] = None# Clayton/Student-t Copula Lower-Tail Contagion Risk (0.01)
    nash_equilibrium_lob_node: Optional[str] = None         # N-Player Non-Cooperative Stochastic Game Nash Equilibrium LOB Node
    zk_stark_proof_certificate: Optional[str] = None        # Post-Quantum zk-STARK Cryptographic Proof Certificate

    # V3.2 Quantum-Biological Upgrades
    nas_evolutionary_fitness_score: Optional[float] = None  # NAS Evolutionary Swarm Model Fitness Score (99.8%)
    calabi_yau_string_resonance: Optional[float] = None     # 10D Calabi-Yau String Field Harmonic Resonance Score (0.96)
    fractional_momentum_order_alpha: Optional[float] = None# Fractional Order Derivative Momentum (d^0.618 P / dt^0.618 = +2.85)
    aco_ant_colony_routing_status: Optional[str] = None # Ant Colony Optimization Pheromone Route Status (ACO_OPTIMAL_PHEROMONE_PATH)
    fhe_homomorphic_ciphertext_hash: Optional[str] = None   # Fully Homomorphic Encryption Ciphertext Hash (0xFHE_CIPHERTEXT_01)

    # V3.3 Real-World Operational Telemetry & Self-Healing Upgrades
    feed_consensus_score: Optional[float] = None            # 3-Source Real-Time Price Median Consensus Score (1.00 = 100%)
    concept_drift_ks_pvalue: Optional[float] = None         # Kolmogorov-Smirnov Concept Drift p-value (0.85 = Nominal)
    execution_slippage_pct: Optional[float] = None          # Real-World Execution Slippage Percentage (0.00%)
    watchdog_failover_status: Optional[str] = None          # Autonomous Failover Watchdog Status (WATCHDOG_NOMINAL_PRIMARY)

    # V4.0 Empirical Convergence
    liquidity_void_distance: Optional[float] = None         # Distance to VPVR High Volume Node (LVN Void)
    tod_execution_window: Optional[str] = None              # Time of Day (ToD) Optimal Window (e.g. 09:15-10:30 AM)
    order_book_skew: Optional[float] = None                 # Dynamic OIB Skew % (e.g. 87.5%)
    gamma_squeeze_state: Optional[str] = None               # Negative Gamma Squeeze Confirmation

    # V4.1 Dark Matter Arbitrage Upgrades
    etf_creation_flow_vortex: Optional[str] = None          # Cross-Exchange ETF Creation Flow (e.g., POSITIVE_INFLOW)
    sector_correlation_convergence: Optional[float] = None  # Sector Component Dispersion/Correlation Score (e.g. 0.88)
    volatility_skew_flattening: Optional[str] = None        # Options Put-Call 25-delta Skew Status (e.g., SKEW_FLATTENED)
    vwap_accumulation_footprint: Optional[str] = None       # Algorithmic TWAP/VWAP Execution Footprint (e.g., DETECTED_72H)
    macro_liquidity_drain_status: Optional[str] = None      # Sovereign Yield Spread & Liquidity (e.g., LIQUIDITY_ABUNDANT)

    regime: Optional[str] = None
    regime_probability: Optional[float] = None

    # Lineage
    model_id: Optional[str] = None
    model_version: str = "TradeMind Core v4.1-Dark Matter"
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
