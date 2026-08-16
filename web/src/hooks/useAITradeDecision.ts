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
  const rawRating = (structured.rating || stock.rating || analysis.consensus || 'HOLD').toUpperCase();
  let rating: AIRating = 'HOLD';
  if (rawRating.includes('STRONG BUY')) rating = 'STRONG BUY';
  else if (rawRating.includes('STRONG SELL')) rating = 'STRONG SELL';
  else if (rawRating.includes('BUY')) rating = 'BUY';
  else if (rawRating.includes('SELL')) rating = 'SELL';

  // 2. Normalize Conviction (0-100)
  const conviction = Math.round(
    (structured.conviction !== undefined && structured.conviction !== null)
    ? structured.conviction : (stock.conviction || stock.ai_investment_score || 0)
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
  const rawTf = (structured.timeframe || stock.timeframe || 'SWING').toUpperCase().replace('_', ' ');
  let timeframe: TimeHorizon = 'SWING';
  if (rawTf.includes('INTRADAY')) timeframe = 'INTRADAY';
  else if (rawTf.includes('SHORT')) timeframe = 'SHORT TERM';
  else if (rawTf.includes('POSITION') || rawTf.includes('MID')) timeframe = 'POSITION';
  else if (rawTf.includes('LONG')) timeframe = 'LONG TERM';

  // 5. Decision Status
  let status: DecisionStatus = (stock.status as DecisionStatus) || 'ACTIVE';
  if (structured.status) status = structured.status as DecisionStatus;
  else if (!stock.analysis && !stock.status) status = 'UNAVAILABLE';

  // 6. Entry Logic
  const parseNum = (val: any) => {
    if (val === null || val === undefined || val === 'Unknown' || val === 'N/A') return undefined;
    const num = Number(val);
    return isNaN(num) ? undefined : num;
  };

  const entry = parseNum(structured.entry) || parseNum(stock.entry_price) || stock.last_price || 0;
  let target = parseNum(structured.target) || parseNum(stock.target_price);
  let stopLoss = parseNum(structured.stop_loss) || parseNum(stock.stop_loss_price);

  // 6.1 Strict Data Adherence (Vision 2.2 Alignment)
  // We do NOT invent targets or stop losses if they are missing from authoritative data.
  // Use existing values or null.

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

  // 8.1 Timestamp Normalization (UTC enforcement)
  const ensureUTC = (ts: any) => {
    if (!ts) return undefined;
    if (typeof ts !== 'string') return ts;
    // If no timezone info, append Z
    if (!ts.includes('Z') && !ts.includes('+') && !ts.includes('-')) {
      return `${ts}Z`;
    }
    return ts;
  };

  return {
    rating,
    conviction,
    riskLevel,
    timeframe,
    status,
    entry,
    target,
    targetRange: structured.target_range,
    stopLoss,
    stopRange: structured.stop_range,
    riskReward: structured.risk_reward || '1:2.0',
    primaryCatalyst: structured.key_catalysts?.[0] || (analysis.recommendations?.[0] as any)?.reasons?.[0],
    keyRisks: structured.key_risks || (analysis.recommendations?.[0] as any)?.risks,
    thesis,
    invalidation: structured.invalidation_point,
    generatedAt: ensureUTC(stock.timestamp),
    validatedAt: ensureUTC(stock.validated_at),
    triggeredAt: ensureUTC(stock.triggered_at),
    triggerPrice: stock.trigger_price,
    triggerCondition: stock.trigger_condition,
    outcomeDate: ensureUTC(stock.outcome_date),
    profitPct: stock.profit_pct,
    mfe: stock.mfe,
    mae: stock.mae,
    updatedAt: ensureUTC(stock.updated_at),
    id: stock.id,
    modelVersion: structured.modelVersion || 'TradeMind Core v2.2',
    drivers,
    events: (stock.events || []).map((e: any) => ({ ...e, timestamp: ensureUTC(e.timestamp) })),

    // F&O Support (RC-5)
    assetClass: stock.asset_class || 'EQUITY',
    underlyingSymbol: stock.underlying_symbol,
    strike: parseNum(stock.strike),
    optionType: stock.option_type,
    expiry: ensureUTC(stock.expiry),
    lotSize: stock.lot_size
  };
};

export const useAITradeDecision = (stock: any): AITradeDecision => {
  return normalizeAITradeDecision(stock);
};
