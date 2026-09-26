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
