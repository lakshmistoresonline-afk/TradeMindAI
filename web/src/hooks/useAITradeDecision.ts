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
  const conviction = Math.round(
    (structured.conviction !== undefined && structured.conviction !== null)
    ? structured.conviction : (stock.ai_investment_score || 0)
  );

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
  const parseNum = (val: any) => {
    if (val === null || val === undefined || val === 'Unknown' || val === 'N/A') return undefined;
    const num = Number(val);
    return isNaN(num) ? undefined : num;
  };

  const entry = parseNum(structured.entry) || stock.last_price;
  const target = parseNum(structured.target);
  const stopLoss = parseNum(structured.stop_loss);

  // 7. Drivers (Explainability)
  let drivers = Array.isArray(structured.drivers) ? structured.drivers : [];
  if (drivers.length === 0 && Array.isArray(analysis.recommendations)) {
     drivers = analysis.recommendations[0]?.reasons?.slice(0, 3) || [];
  }
  drivers = (drivers as any[]).filter(d => typeof d === 'string' && !d.includes('{'));

  // 8. Robust Thesis/Reasoning
  let thesis = structured.thesis || analysis.consensus || 'Analyzing session dynamics...';

  // Prevent raw JSON or Code from leaking into UI
  const codeMarkers = ['{', '```', 'import ', 'def ', 'return ', 'json.'];
  const isLikelyCode = codeMarkers.some(m => thesis.includes(m));

  if (isLikelyCode) {
    if (structured.thesis && !structured.thesis.includes('{')) {
      thesis = structured.thesis;
    } else {
      // Try to extract thesis from raw string if parsing failed
      const match = thesis.match(/["']thesis["']:\s*["'](.*?)["']/);
      thesis = (match && match[1]) ? match[1] : 'Synthesis in progress...';
    }
  }

  // Final trim to remove any remaining artifacts
  if (thesis.length > 500) thesis = thesis.substring(0, 497) + '...';

  return {
    rating,
    conviction,
    riskLevel,
    timeframe,
    status,
    entry,
    target,
    stopLoss,
    riskReward: structured.risk_reward || '1:2.0',
    primaryCatalyst: structured.key_catalysts?.[0] || (analysis.recommendations?.[0] as any)?.reasons?.[0],
    keyRisks: structured.key_risks || (analysis.recommendations?.[0] as any)?.risks,
    thesis,
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
