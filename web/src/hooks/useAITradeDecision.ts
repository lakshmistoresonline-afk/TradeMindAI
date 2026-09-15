import { AITradeDecision, AIRating, RiskLevel, TimeHorizon, DecisionStatus } from '../types/domain';

/**
 * Canonical Signal Normalizer (V2.3)
 * Ensures consistent interpretation of backend signals across all pages.
 */
export const normalizeAITradeDecision = (signal: any): AITradeDecision => {
  if (!signal) return {
    rating: 'HOLD',
    conviction: 0,
    riskLevel: 'MODERATE',
    timeframe: 'SWING',
    status: 'UNAVAILABLE'
  };

  const structured = signal.structured_consensus || {};
  const analysis = signal.analysis || {};

  // 1. Normalize Rating
  const rawRating = String(structured.rating || signal.rating || analysis.consensus || 'HOLD').toUpperCase();
  let rating: AIRating = 'HOLD';
  if (rawRating.includes('STRONG BUY')) rating = 'STRONG BUY';
  else if (rawRating.includes('STRONG SELL')) rating = 'STRONG SELL';
  else if (rawRating.includes('BUY')) rating = 'BUY';
  else if (rawRating.includes('SELL')) rating = 'SELL';

  // 2. Normalize Conviction (0-100)
  const conviction = Math.round(
    (structured.conviction !== undefined && structured.conviction !== null)
    ? structured.conviction : (signal.conviction || signal.ai_investment_score || 0)
  );

  // 3. Normalize Risk Level
  let riskLevel: RiskLevel = 'MODERATE';
  const rawRisk = String(structured.riskLevel || signal.risk_mode || '').toUpperCase();
  if (rawRisk === 'LOW' || rawRisk === 'RISK_OFF') riskLevel = 'LOW';
  else if (rawRisk === 'HIGH' || rawRisk === 'RISK_ON') riskLevel = 'HIGH';
  else {
    const beta = signal.beta || 1.0;
    if (beta > 1.2) riskLevel = 'HIGH';
    else if (beta < 0.8) riskLevel = 'LOW';
  }

  // 4. Normalize Timeframe (Canonical: SHORT, SWING, LONG)
  const rawTf = String(structured.timeframe || signal.timeframe || 'SWING').toUpperCase().replace(/_/g, ' ').replace(/-/g, ' ');
  let timeframe: TimeHorizon = 'SWING';
  if (rawTf.includes('SHORT')) timeframe = 'SHORT';
  else if (rawTf.includes('SWING')) timeframe = 'SWING';
  else if (rawTf.includes('LONG')) timeframe = 'LONG';
  else if (rawTf.includes('POSITION') || rawTf.includes('MID')) timeframe = 'LONG';
  else if (rawTf.includes('INTRADAY')) timeframe = 'SHORT';

  // 5. Decision Status
  let status: DecisionStatus = (signal.status as DecisionStatus) || 'ACTIVE';
  if (structured.status) status = structured.status as DecisionStatus;
  else if (!signal.analysis && !signal.status) status = 'UNAVAILABLE';

  // 6. Entry/Price Logic
  const parseNum = (val: any) => {
    if (val === null || val === undefined || val === 'Unknown' || val === 'N/A') return undefined;
    const num = Number(val);
    return isNaN(num) ? undefined : num;
  };

  const entry = parseNum(structured.entry) || parseNum(signal.entry_price) || signal.last_price || 0;
  const target = parseNum(structured.target) || parseNum(signal.target_price);
  const stopLoss = parseNum(structured.stop_loss) || parseNum(signal.stop_price);
  const current = parseNum(signal.current_price) || parseNum(signal.last_price);

  // 7. Drivers
  let drivers = Array.isArray(structured.drivers) ? structured.drivers : [];
  if (drivers.length === 0 && Array.isArray(analysis.recommendations)) {
     drivers = analysis.recommendations[0]?.reasons?.slice(0, 3) || [];
  }
  drivers = (drivers as any[]).filter(d => typeof d === 'string' && !d.includes('{'));

  // 8. Thesis
  let thesis = structured.thesis || signal.exit_reason || analysis.consensus || 'Analyzing institutional order flow...';
  if (thesis.length > 500) thesis = thesis.substring(0, 497) + '...';

  // 9. Quality Class (Strict V2.3 Classification)
  // Backend quality_class is the authority. Fallback is deterministic.
  const qualityClass = signal.quality_class || (timeframe === 'SWING' ? 'PRIMARY' : timeframe === 'LONG' ? 'SELECTIVE' : 'EXPERIMENTAL');

  // 10. Timing (UTC Enforcement)
  const ensureUTC = (ts: any) => {
    if (!ts) return undefined;
    if (typeof ts !== 'string') return ts;
    return ts.includes('Z') || ts.includes('+') || ts.includes('-') ? ts : `${ts}Z`;
  };

  return {
    id: signal.id,
    rating,
    conviction,
    riskLevel,
    timeframe,
    status,
    entry,
    target,
    stopLoss,
    riskReward: signal.risk_reward_ratio ? `1:${signal.risk_reward_ratio.toFixed(1)}` : '1:2.5',
    expectedValue: parseNum(signal.expected_value),
    thesis,
    drivers,
    generatedAt: ensureUTC(signal.created_at || signal.timestamp),
    validatedAt: ensureUTC(signal.validated_at),
    updatedAt: ensureUTC(signal.updated_at),
    normalizedCurrentPrice: current,
    qualityClass: qualityClass as any,
    assetClass: signal.asset_class || 'EQUITY',
    underlyingSymbol: signal.symbol,
    priceStatus: signal.data_quality_status || 'FRESH'
  };
};

export const useAITradeDecision = (stock: any): AITradeDecision => {
  return normalizeAITradeDecision(stock);
};
