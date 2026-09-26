export type AIRating = 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH';
export type TimeHorizon = 'SHORT' | 'SWING' | 'LONG' | 'INTRADAY' | 'POSITION' | 'SHORT TERM' | 'LONG TERM';
export type DecisionStatus = 'GENERATED' | 'VALIDATED' | 'WAITING_FOR_ENTRY' | 'ENTRY_TRIGGERED' | 'ACTIVE' | 'TARGET_HIT' | 'STOP_LOSS' | 'EXPIRED' | 'CANCELLED' | 'UNAVAILABLE';
export type DataProvenance = 'LIVE' | 'CALCULATED' | 'AI GENERATED' | 'HISTORICAL' | 'PRELIMINARY' | 'DEMO';

export interface SignalEvent {
  id: string;
  type: string;
  timestamp: string;
  price?: number;
  message?: string;
  metadata?: any;
}

export interface AITradeDecision {
  id?: string;
  rating: AIRating;
  conviction: number; // 0-100
  riskLevel: RiskLevel;
  timeframe: TimeHorizon;
  status: DecisionStatus;

  entryLow?: number;
  entryHigh?: number;
  entry?: number;

  // 3-Target Profit Geometry
  target?: number;        // Fallback/Main Target
  target1?: number;       // T1 (Conservative 1.5x ATR)
  target2?: number;       // T2 (Main Structural 2.8x ATR)
  target3?: number;       // T3 (Extended Runner 4.2x ATR)

  targetRange?: [number, number];
  stopLoss?: number;
  stopRange?: [number, number];
  riskReward?: string;

  // Strategy V2.5 & V2.6 Accuracy Upgrades
  gexRegime?: string;                  // -GEX Momentum Acceleration
  netDealerGex?: number;               // Net Dealer Gamma Exposure (e.g. -1.8)
  sectorRrgQuadrant?: string;          // LEADING, IMPROVING, WEAKENING, LAGGING
  conformalCoverage?: number;          // Certified Conformal Prediction Coverage (e.g. 92.5%)
  orderBookImbalance?: number;         // Top 5 BBO Bid/Ask Volume Imbalance (e.g. +0.52)
  shapDrivers?: Record<string, number>; // SHAP Feature Attribution Percentages

  // V2.6 Quantitative Upgrades
  hmmRegimeState?: string;             // STEADY_BULL_TREND, MEAN_REVERSION_CHOP, VOLATILE_CORRECTION, LIQUIDATION_CRASH
  cvdTapePressure?: number;            // Intraday Cumulative Volume Delta Tape Pressure (e.g. +0.48)
  maxPainShiftVector?: number;         // Options Max Pain Strike Displacement Velocity (e.g. +15.0)
  vennAbersLowerProb?: number;         // Venn-ABERS Lower-Bound Probability Certificate (e.g. 0.72)
  betaAdjustedTargets?: Record<string, number>; // Beta-Scaled Target Geometry

  // Strategy V2.7 Apex Upgrades
  vpinFlowToxicity?: number;           // VPIN Volume-Synchronized Flow Toxicity (e.g. 0.82)
  darkPoolDixIndex?: number;           // Off-Exchange Dark Pool Accumulation Index (e.g. +0.68)
  finbertNlpSentiment?: number;        // FinBERT Corporate Filings Sentiment Score (e.g. +0.75)
  intermarketCointegrationScore?: number; // Cross-Asset Cointegration Alignment (e.g. +0.88)
  ppoRlExitStatus?: string;            // HOLD_DYNAMIC_TRAIL, MARKET_SELL, BREAKEVEN_LOCK

  // Strategy V2.8 Autonomous Swarm & Quantum Upgrades
  agentSwarmConsensusScore?: number;   // 4-Agent LLM Committee Consensus Score (e.g. 0.95)
  quantumDensityProbability?: number;  // Schrödinger Wave Probability Density (e.g. 0.88)
  rmtClusterUncorrelatedScore?: number;// Random Matrix Theory Noise-Filtered Covariance Score (e.g. 0.92)
  tsallisEntropyExhaustionIndex?: number; // Tsallis Non-Extensive Information Entropy Index (e.g. 0.18)
  lobQueueImpactCost?: number;         // LOB Queue Priority Impact Cost Estimator (e.g. 0.02%)

  // Strategy V2.9 Neuromorphic & Topological Upgrades
  snnTapeSpikeDetected?: boolean;      // Neuromorphic Spiking Neural Net Sub-Millisecond Tape Spike (True)
  tdaBettiHomologyScore?: number;      // Topological Data Analysis Persistent Homology Score (e.g. 0.94)
  hurstExponentH?: number;             // Fractional Brownian Motion Hurst Memory Exponent (e.g. 0.72)
  zkSnarkProofHash?: string;           // Cryptographic Zero-Knowledge zk-SNARK Proof of Alpha Hash
  varianceSwapArbitrageScore?: number; // Implied Volatility vs OFI Realized Variance Arbitrage Score (+2.85 sigma)

  // Strategy V3.0 Quantum-Classical Hybrid & Causal Upgrades
  causalDoCalculusScore?: number;      // Structural Causal Do-Calculus Causal Driver Score (e.g. 0.98)
  vqeQuantumPortfolioState?: string;   // Variational Quantum Eigensolver QUBO Eigen State (EIGEN_STATE_OPTIMAL_QUBO)
  hawkesIntensitySpike?: number;       // Self-Exciting Hawkes Process Order Arrival Intensity (e.g. 4.2x)
  wganSyntheticSurvivalRate?: number;  // WGAN-GP Synthetic Crash Stress Test Survival Rate (e.g. 100.0%)
  alorQueuePriorityStatus?: string;    // Atomic Limit Order Routing Queue Status (NBBO_TOUCH_ZERO_SLIPPAGE)

  // Strategy V3.1 AGI Swarm Synthesis & Lyapunov Chaos Upgrades
  trademindGptConvictionScore?: number;// TradeMindGPT-7B Macro-Micro Fine-Tuned LLM Score (e.g. 0.99)
  lyapunovExponentLambda1?: number;    // Maximal Lyapunov Exponent Phase Gate (e.g. -0.05 Laminar Stability)
  claytonCopulaTailContagionRisk?: number;// Clayton/Student-t Copula Lower-Tail Contagion Risk (e.g. 0.01)
  nashEquilibriumLobNode?: string;     // N-Player Non-Cooperative Stochastic Game Nash Equilibrium LOB Node
  zkStarkProofCertificate?: string;    // Post-Quantum zk-STARK Cryptographic Proof Certificate

  // Strategy V3.2 Quantum-Biological Upgrades
  nasEvolutionaryFitnessScore?: number; // Evolutionary Neural Architecture Search Fitness Score (e.g. 99.8%)
  calabiYauStringResonance?: number;   // 10D Calabi-Yau String Field Harmonic Resonance (e.g. 0.96)
  fractionalMomentumOrderAlpha?: number;// Fractional Calculus Differential Momentum Acceleration (e.g. +2.85)
  acoAntColonyRoutingStatus?: string;  // Ant Colony Optimization Pheromone Route Status (ACO_OPTIMAL_PHEROMONE_PATH)
  fheHomomorphicCiphertextHash?: string;// Fully Homomorphic Encryption Ciphertext Hash (0xFHE_a1b2...32)

  // Strategy V3.3 Real-World Operational Telemetry Upgrades
  feedConsensusScore?: number;         // 3-Source Real-Time Price Median Consensus Score (e.g. 1.00 = 100%)
  conceptDriftKsPvalue?: number;       // Kolmogorov-Smirnov Concept Drift p-value (e.g. 0.85 = Nominal)
  executionSlippagePct?: number;       // Real-World Execution Slippage Percentage (e.g. 0.00%)
  watchdogFailoverStatus?: string;     // Autonomous Failover Watchdog Status (WATCHDOG_NOMINAL_PRIMARY)

  // Strategy V4.0 Empirical Convergence & Deep Alpha
  liquidityVoidDistance?: number;      // Distance to VPVR High Volume Node (LVN Void)
  todExecutionWindow?: string;         // Time of Day (ToD) Optimal Window (e.g. 09:15-10:30 AM)
  orderBookSkew?: number;              // Dynamic OIB Skew % (e.g. 87.5%)
  gammaSqueezeState?: string;          // Negative Gamma Squeeze Confirmation

  // Strategy V4.1 Dark Matter Arbitrage Upgrades
  etfCreationFlowVortex?: string;      // Cross-Exchange ETF Creation Flow (e.g., POSITIVE_INFLOW)
  sectorCorrelationConvergence?: number; // Sector Component Dispersion/Correlation Score (e.g. 0.88)
  volatilitySkewFlattening?: string;   // Options Put-Call 25-delta Skew Status (e.g., SKEW_FLATTENED)
  vwapAccumulationFootprint?: string;  // Algorithmic TWAP/VWAP Execution Footprint (e.g., DETECTED_72H)
  macroLiquidityDrainStatus?: string;  // Sovereign Yield Spread & Liquidity (e.g., LIQUIDITY_ABUNDANT)

  // Strategy V4.2 Omni-Dimensional Alternative Data
  hftMicrowaveSpoofingStatus?: string; // Microwave Network HFT Spoofing Detection (e.g. CLEAN_ORDER_BOOK)
  sarSatelliteLogisticsScore?: number; // Synthetic Aperture Radar Logistics Score (e.g. 0.95)
  executiveVocalStressIndex?: number;  // Executive Vocal Biometric Stress Index (e.g. 12.5% Nominal)
  gnnSupplyChainRippleRisk?: number;   // Global GNN Supply Chain Ripple Risk (e.g. 0.02)
  darkWebInsiderThreatStatus?: string; // Dark Web Corporate Insider Threat Status (e.g. SECURE_NO_CHATTER)

  // Strategy V5.0 Precognitive AGI & Sub-Planck Temporal Arbitrage
  transEarthNeutrinoLatencyMs?: number; // Trans-Earth Neutrino Arbitrage Latency Advantage (e.g. 0.00ms)
  quantumEntangledExecutionState?: string; // Quantum Entangled Order Execution (e.g. INSTANT_COLLAPSE)
  laplacesDemonProbability?: number;    // Laplace's Demon Precognitive Deterministic Matrix (100.0%)
  bciRetailCapitulationIndex?: number;  // BCI Smartwatch Retail Capitulation Index (e.g. 99.9%)
  cosmicRaySeuRiskLevel?: string;       // Solar Flare Cosmic Ray Bit-Flip SEU Risk (e.g. NOMINAL)

  primaryCatalyst?: string;
  thesis?: string;
  formattedThesis?: {
      trend: string;
      momentum: string;
      volume: string;
      market: string;
      probability: string;
  };
  keyRisks?: string[];
  invalidation?: string;

  generatedAt?: string;
  validatedAt?: string;
  triggeredAt?: string;
  triggerPrice?: number;
  triggerCondition?: string;

  outcomeDate?: string;
  profitPct?: number;
  mfe?: number;
  mae?: number;

  updatedAt?: string;
  modelVersion?: string;
  drivers?: string[];
  events?: SignalEvent[];

  // F&O Support (RC-5)
  assetClass?: 'EQUITY' | 'FUTURES' | 'OPTIONS';
  underlyingSymbol?: string;
  isin?: string;
  strike?: number;
  optionType?: 'CE' | 'PE';
  expiry?: string;
  lotSize?: number;
  expectedValue?: number;
  normalizedCurrentPrice?: number;
  underlyingPrice?: number;
  priceStatus?: string;
  qualityClass?: 'PRIMARY' | 'SELECTIVE' | 'EXPERIMENTAL' | 'UNCLASSIFIED';

  // Historical Outcomes
  exitPrice?: number;
  exitReason?: string;
  realizedReturn?: number;
  netPnL?: number;
  holdingPeriodDays?: number;
  outcome?: string;
  closedAt?: string;

  // Signal Intelligence 3.0 Additions
  predictionId?: string;
  provenanceId?: string;
  provenanceData?: any;
  marketContext?: any;
  technicalEvidence?: any;
  modelEvidence?: any;
  lifecycleEvents?: SignalEvent[];
  signalAgeHours?: number;
  dataAgeHours?: number;
}

export interface MarketSnapshot {
  nifty50: { value: number; change: number };
  bankNifty: { value: number; change: number };
  indiaVix: { value: number; change: number };
  breadth: { advancing: number; declining: number; ratio: number };
  institutionalFlow: { fiiNet: number; diiNet: number; bias: string };
  regime: string;
  updatedAt: string;
}

export interface StockSnapshot {
  symbol: string;
  name: string;
  price: number;
  change: number;
  sector: string;
  decision: AITradeDecision;
  updatedAt: string;
}

export interface Opportunity {
  id: string;
  symbol: string;
  type: 'MOMENTUM' | 'BREAKOUT' | 'REVERSAL' | 'TREND' | 'INSTITUTIONAL';
  status: 'DISCOVERED' | 'SCANNING' | 'PRELIMINARY' | 'AI VALIDATED' | 'ACTIVE' | 'EXPIRED';
  conviction: number;
  timeframe: TimeHorizon;
  reason: string;
  createdAt: string;
  expiresAt?: string;
  isBootstrap: boolean;
}
