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

  // Strategy V2.5 Accuracy Upgrades
  gexRegime?: string;                  // -GEX Momentum Acceleration
  netDealerGex?: number;               // Net Dealer Gamma Exposure (e.g. -1.8)
  sectorRrgQuadrant?: string;          // LEADING, IMPROVING, WEAKENING, LAGGING
  conformalCoverage?: number;          // Certified Conformal Prediction Coverage (e.g. 92.5%)
  orderBookImbalance?: number;         // Top 5 BBO Bid/Ask Volume Imbalance (e.g. +0.52)
  shapDrivers?: Record<string, number>; // SHAP Feature Attribution Percentages

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
