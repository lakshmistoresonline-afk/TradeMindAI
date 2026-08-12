export type AIRating = 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH';
export type TimeHorizon = 'INTRADAY' | 'SWING' | 'POSITION' | 'LONG TERM';
export type DecisionStatus = 'PENDING' | 'ANALYZING' | 'VALIDATED' | 'ACTIVE' | 'EXPIRED' | 'UNAVAILABLE';
export type DataProvenance = 'LIVE' | 'CALCULATED' | 'AI GENERATED' | 'HISTORICAL' | 'PRELIMINARY' | 'DEMO';

export interface AITradeDecision {
  rating: AIRating;
  conviction: number; // 0-100
  riskLevel: RiskLevel;
  timeframe: TimeHorizon;
  status: DecisionStatus;

  entryLow?: number;
  entryHigh?: number;
  entry?: number;
  target?: number;
  targetRange?: [number, number];
  stopLoss?: number;
  stopRange?: [number, number];
  riskReward?: string;

  primaryCatalyst?: string;
  thesis?: string;
  keyRisks?: string[];
  invalidation?: string;

  generatedAt?: string;
  updatedAt?: string;
  modelVersion?: string;
  drivers?: string[];
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
