import { AITradeDecision, AIRating, RiskLevel, TimeHorizon, DecisionStatus } from '../types/domain';

export const normalizeAITradeDecision = (stock: any): AITradeDecision => {
  if (!stock) return {
    rating: 'HOLD',
    conviction: 0,
    riskLevel: 'MODERATE',
    timeframe: 'SWING',
    status: 'UNAVAILABLE'
  };

  const analysis = stock.analysis || {};
  const structured = stock.structured_consensus || {};

  // 1. Normalize Rating
  const rawRating = (structured.rating || analysis.consensus || 'HOLD').toUpperCase();
  let rating: AIRating = 'HOLD';
  if (rawRating.includes('STRONG BUY')) rating = 'STRONG BUY';
  else if (rawRating.includes('STRONG SELL')) rating = 'STRONG SELL';
  else if (rawRating.includes('BUY')) rating = 'BUY';
  else if (rawRating.includes('SELL')) rating = 'SELL';

  // 2. Normalize Conviction (0-100)
  const conviction = Math.round(structured.conviction || stock.ai_investment_score || 0);

  // 3. Normalize Risk Level
  let riskLevel: RiskLevel = 'MODERATE';
  const rawRisk = (structured.riskLevel || '').toUpperCase();
  if (rawRisk === 'LOW') riskLevel = 'LOW';
  else if (rawRisk === 'HIGH') riskLevel = 'HIGH';
  else {
    const beta = stock.beta || 1.0;
    if (beta > 1.2) riskLevel = 'HIGH';
    else if (beta < 0.8) riskLevel = 'LOW';
  }

  // 4. Normalize Timeframe
  const rawTf = (structured.timeframe || 'SWING').toUpperCase();
  let timeframe: TimeHorizon = 'SWING';
  if (rawTf === 'INTRADAY') timeframe = 'INTRADAY';
  else if (rawTf === 'POSITION' || rawTf === 'MID_TERM') timeframe = 'POSITION';
  else if (rawTf === 'LONG_TERM' || rawTf === 'LONG TERM') timeframe = 'LONG TERM';

  // 5. Decision Status
  let status: DecisionStatus = 'ACTIVE';
  if (!stock.analysis) status = 'UNAVAILABLE';
  else if (structured.status) status = structured.status as DecisionStatus;

  // 6. Entry Logic
  const entryLow = structured.entryZone?.low;
  const entryHigh = structured.entryZone?.high;
  const entry = structured.entry || stock.last_price;

  // 7. Drivers (Explainability)
  const drivers = structured.drivers || (analysis.recommendations?.[0]?.reasons ? analysis.recommendations[0].reasons.slice(0, 3) : []);

  return {
    rating,
    conviction,
    riskLevel,
    timeframe,
    status,
    entryLow,
    entryHigh,
    entry,
    target: structured.target,
    stopLoss: structured.stop_loss,
    riskReward: structured.risk_reward || '1:2.0',
    primaryCatalyst: structured.key_catalysts?.[0] || analysis.recommendations?.[0]?.reasons?.[0],
    keyRisks: structured.key_risks || analysis.recommendations?.[0]?.risks,
    thesis: structured.thesis || analysis.consensus,
    invalidation: structured.invalidation_point,
    generatedAt: stock.updated_at,
    updatedAt: stock.updated_at,
    modelVersion: structured.modelVersion || 'TradeMind Core v2.0',
    drivers
  };
};

export const useAITradeDecision = (stock: any): AITradeDecision => {
  return normalizeAITradeDecision(stock);
};
