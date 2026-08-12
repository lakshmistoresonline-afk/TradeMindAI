export type AIRating = 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH';
export type TimeHorizon = 'INTRADAY' | 'SWING' | 'POSITION' | 'LONG TERM';
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
  validatedAt?: string;
  triggeredAt?: string;
  triggerPrice?: number;

  outcomeDate?: string;
  profitPct?: number;
  mfe?: number;
  mae?: number;

  updatedAt?: string;
  modelVersion?: string;
  drivers?: string[];
  events?: SignalEvent[];
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
