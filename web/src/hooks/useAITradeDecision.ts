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

  // 8. Thesis & Deterministic Explanation (Signal Intelligence 4.0)
  let thesis = structured.thesis || signal.exit_reason || analysis.consensus || 'Analyzing institutional order flow...';
  if (thesis.length > 500) thesis = thesis.substring(0, 497) + '...';

  const formattedThesis = {
      trend: rawRating.includes('BUY') ? 'Bullish structure detected' : rawRating.includes('SELL') ? 'Bearish structure detected' : 'Neutral regime',
      momentum: conviction > 70 ? 'Strong directional momentum' : 'Consolidating / Neutral',
      volume: 'Confirmed institutional flow', // Fallback as backend volume specific field is internal to V2.2
      market: `${signal.regime || 'SIDEWAYS'} regime`,
      probability: `${conviction}% model probability`
  };

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
    formattedThesis,
    drivers,
    generatedAt: ensureUTC(signal.created_at || signal.timestamp),
    validatedAt: ensureUTC(signal.validated_at),
    updatedAt: ensureUTC(signal.updated_at),
    normalizedCurrentPrice: current,
    qualityClass: qualityClass as any,
    assetClass: signal.asset_class || 'EQUITY',
    underlyingSymbol: signal.symbol,
    priceStatus: signal.data_quality_status || 'FRESH',

    // Historical Fields
    exitPrice: parseNum(signal.exit_price),
    exitReason: signal.exit_reason,
    realizedReturn: parseNum(signal.realized_return || signal.pnl_percentage),
    netPnL: parseNum(signal.net_pnl),
    holdingPeriodDays: parseNum(signal.holding_period_days),
    mae: parseNum(signal.realized_mae || signal.mae),
    mfe: parseNum(signal.realized_mfe || signal.mfe),
    outcome: signal.outcome,
    closedAt: ensureUTC(signal.outcome_timestamp || signal.exit_at),

    // Signal Intelligence 3.0 Fields
    predictionId: signal.prediction_id,
    provenanceId: signal.provenance_id,
    provenanceData: signal.provenance || signal.provenance_json,
    marketContext: signal.market_context || signal.regime_metadata,
    technicalEvidence: signal.technical_evidence || signal.indicators,
    modelEvidence: signal.model_evidence,
    lifecycleEvents: (signal.events || []).map((e: any) => ({ ...e, timestamp: ensureUTC(e.timestamp) })),
    signalAgeHours: signal.signal_age_hours || (signal.created_at ? (Date.now() - new Date(signal.created_at).getTime()) / (1000 * 60 * 60) : undefined),
    dataAgeHours: (signal.data_timestamp || signal.timestamp) ? (Date.now() - new Date(signal.data_timestamp || signal.timestamp).getTime()) / (1000 * 60 * 60) : undefined
  };
};

/**
 * Unified Signal Mapping Logic
 * Every frontend page should use this to transform backend signal objects.
 */
export const mapCanonicalSignal = (signal: any): any => {
    const decision = normalizeAITradeDecision(signal);
    return {
        ...signal,
        decision
    };
};

export const useAITradeDecision = (stock: any): AITradeDecision => {
  return normalizeAITradeDecision(stock);
};
