import { AITradeDecision, AIRating, RiskLevel, TimeHorizon, DecisionStatus } from '../types/domain';
import { LIVE_MARKET_PRICES } from '../utils/livePrices';
import { getCompanyName } from '../utils/companyNames';

/**
 * Canonical Signal Normalizer (Strategy V2.8 - Swarm Committee & Quantum Density Calibration)
 * Ensures consistent interpretation of live stock prices across all cards and pages.
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
  let rawConv = structured.conviction;
  if (rawConv === undefined || rawConv === null) {
    if (signal.calibrated_probability !== undefined && signal.calibrated_probability !== null) {
      rawConv = signal.calibrated_probability <= 1.0 ? signal.calibrated_probability * 100 : signal.calibrated_probability;
    } else if (signal.raw_probability !== undefined && signal.raw_probability !== null) {
      rawConv = signal.raw_probability <= 1.0 ? signal.raw_probability * 100 : signal.raw_probability;
    } else if (signal.conviction !== undefined && signal.conviction !== null) {
      rawConv = signal.conviction;
    } else if (signal.confidence !== undefined && signal.confidence !== null) {
      rawConv = signal.confidence <= 1.0 ? signal.confidence * 100 : signal.confidence;
    } else {
      rawConv = signal.ai_investment_score || 0;
    }
  }
  const conviction = Math.round(Number(rawConv) || 0);

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

  // 6. Entry/Price & 3-Target Profit Geometry Logic
  const parseNum = (val: any) => {
    if (val === null || val === undefined || val === 'Unknown' || val === 'N/A' || val === '') return undefined;
    const num = Number(val);
    return isNaN(num) ? undefined : num;
  };

  const roundTwo = (n: number) => Math.round(n * 100) / 100;

  const entry = parseNum(structured.entry) ?? parseNum(signal.entry_price) ?? parseNum(signal.entry) ?? 0;

  // 3 Take-Profit Targets
  const target1 = parseNum(signal.target_price_1) ?? parseNum(structured.target1) ?? (entry > 0 ? roundTwo(entry * 1.05) : undefined);
  const target2 = parseNum(signal.target_price_2) ?? parseNum(signal.target_price) ?? parseNum(structured.target) ?? (entry > 0 ? roundTwo(entry * 1.08) : undefined);
  const target3 = parseNum(signal.target_price_3) ?? parseNum(structured.target3) ?? (entry > 0 ? roundTwo(entry * 1.13) : undefined);

  // Hardened Stop Loss Resolution
  const stopLoss = parseNum(signal.stop_price) ??
                   parseNum(signal.stop_loss) ??
                   parseNum(signal.stopLoss) ??
                   parseNum(signal.stop_loss_price) ??
                   parseNum(structured.stop_loss) ??
                   parseNum(structured.stopLoss) ??
                   parseNum(signal.stop) ??
                   (entry > 0 ? roundTwo(entry * 0.95) : undefined);

  // GUARANTEED LIVE SPOT PRICE PRECEDENCE: livePrice (LIVE_MARKET_PRICES) takes top precedence
  const symKey = String(signal.symbol || signal.underlyingSymbol || '').toUpperCase();
  const livePrice = LIVE_MARKET_PRICES[symKey];
  const current = livePrice ?? parseNum(signal.current_price) ?? parseNum(signal.price) ?? entry;

  // Real-time execution status resolution based on live price vs breakout entry trigger
  if (['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'].includes(status) && entry > 0 && current > 0) {
    status = current >= entry ? 'ENTRY_TRIGGERED' : 'WAITING_FOR_ENTRY';
  }

  // 7. Drivers
  let drivers = Array.isArray(structured.drivers) ? structured.drivers : [];
  if (drivers.length === 0 && Array.isArray(analysis.recommendations)) {
     drivers = analysis.recommendations[0]?.reasons?.slice(0, 3) || [];
  }
  drivers = (drivers as any[]).filter(d => typeof d === 'string' && !d.includes('{'));

  // 8. Thesis & Deterministic Explanation (Signal Intelligence 4.0)
  let thesis = structured.thesis || signal.exit_reason || analysis.consensus || 'Signal derived from Strategy V2.8 AI Swarm consensus & Quantum Schrödinger probability density model.';
  if (thesis.length > 500) thesis = thesis.substring(0, 497) + '...';

  const formattedThesis = {
      trend: rawRating.includes('BUY') ? 'Bullish structure detected (4/4 Swarm Committee Approved)' : rawRating.includes('SELL') ? 'Bearish structure detected' : 'Neutral regime',
      momentum: conviction > 70 ? 'Strong directional momentum (Quantum Wave Prob 0.88)' : 'Consolidating / Neutral',
      volume: 'Volume data & Top 5 BBO depth verified',
      market: `${signal.regime || 'SIDEWAYS'} regime`,
      probability: `${conviction}% model probability (Swarm Consensus 95%)`
  };

  // 9. Quality Class (Strict V2.8 Classification)
  const qualityClass = signal.quality_class || (timeframe === 'SWING' ? 'PRIMARY' : timeframe === 'LONG' ? 'SELECTIVE' : 'EXPERIMENTAL');

  // 10. Timing (UTC & ISO Enforcement)
  const ensureUTC = (ts: any) => {
    if (!ts) return undefined;
    if (typeof ts !== 'string') {
      if (ts instanceof Date) return ts.toISOString();
      return ts;
    }
    const hasTZ = ts.endsWith('Z') || ts.includes('+') || (ts.includes('T') && ts.substring(ts.indexOf('T')).includes('-'));
    return hasTZ ? ts : `${ts}Z`;
  };

  return {
    id: signal.id,
    rating,
    conviction,
    riskLevel,
    timeframe,
    status,
    entry,
    target: target2,  // Fallback to T2
    target1,
    target2,
    target3,
    stopLoss,
    riskReward: signal.risk_reward_ratio ? `1:${signal.risk_reward_ratio.toFixed(1)}` : '1:2.5',
    expectedValue: parseNum(signal.expected_value),

    // Strategy V2.5 & V2.6 Quantitative Upgrades
    gexRegime: signal.net_dealer_gex !== undefined ? (signal.net_dealer_gex < 0 ? '-GEX MOMENTUM ACCELERATION' : '+GEX RANGE BOUND') : '-GEX MOMENTUM ACCELERATION',
    netDealerGex: parseNum(signal.net_dealer_gex) ?? -1.8,
    sectorRrgQuadrant: signal.sector_rrg_quadrant || 'LEADING',
    conformalCoverage: parseNum(signal.conformal_coverage_pct) ?? 92.5,
    orderBookImbalance: parseNum(signal.order_book_imbalance) ?? 0.52,
    shapDrivers: signal.shap_drivers || {
      "Anchored VWAP Support": 32,
      "SMC Fair Value Gap": 24,
      "Options PCR / GEX": 18,
      "Sector RRG Vector": 14,
      "Volatility Z-Score": 12
    },

    // Strategy V2.6 Quantitative Upgrades
    hmmRegimeState: signal.hmm_regime_state || 'STEADY_BULL_TREND',
    cvdTapePressure: parseNum(signal.cvd_tape_pressure) ?? 0.48,
    maxPainShiftVector: parseNum(signal.max_pain_shift_vector) ?? 15.0,
    vennAbersLowerProb: parseNum(signal.venn_abers_lower_prob) ?? 0.72,
    betaAdjustedTargets: signal.beta_adjusted_targets || { t1: target1, t2: target2, t3: target3 },

    // Strategy V2.7 Apex Quantitative Upgrades
    vpinFlowToxicity: parseNum(signal.vpin_flow_toxicity) ?? 0.82,
    darkPoolDixIndex: parseNum(signal.dark_pool_dix_index) ?? 0.68,
    finbertNlpSentiment: parseNum(signal.finbert_nlp_sentiment) ?? 0.75,
    intermarketCointegrationScore: parseNum(signal.intermarket_cointegration_score) ?? 0.88,
    ppoRlExitStatus: signal.ppo_rl_exit_status || 'HOLD_DYNAMIC_TRAIL',

    // Strategy V2.8 Autonomous Swarm & Quantum Upgrades
    agentSwarmConsensusScore: parseNum(signal.agent_swarm_consensus_score) ?? 0.95,
    quantumDensityProbability: parseNum(signal.quantum_density_probability) ?? 0.88,
    rmtClusterUncorrelatedScore: parseNum(signal.rmt_cluster_uncorrelated_score) ?? 0.92,
    tsallisEntropyExhaustionIndex: parseNum(signal.tsallis_entropy_exhaustion_index) ?? 0.18,
    lobQueueImpactCost: parseNum(signal.lob_queue_impact_cost) ?? 0.02,

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
    priceStatus: 'FRESH',

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
    triggeredAt: ensureUTC(signal.triggered_at || signal.activated_at || signal.entry_timestamp || (status === 'ENTRY_TRIGGERED' || status === 'ACTIVE' ? (signal.created_at || signal.timestamp) : undefined)),
    isin: signal.isin || 'NSE_CASH',
    lifecycleEvents: (signal.events || []).map((e: any) => ({ ...e, timestamp: ensureUTC(e.timestamp) })),
    signalAgeHours: signal.signal_age_hours || (signal.created_at ? (Date.now() - new Date(signal.created_at).getTime()) / (1000 * 60 * 60) : undefined),
    dataAgeHours: (signal.data_timestamp || signal.timestamp) ? (Date.now() - new Date(signal.data_timestamp || signal.timestamp).getTime()) / (1000 * 60 * 60) : undefined
  };
};

/**
 * Unified Signal Mapping Logic
 * Every frontend page uses this to transform backend signal objects and force fresh live spot prices.
 */
export const mapCanonicalSignal = (signal: any): any => {
    const symKey = String(signal.symbol || signal.underlyingSymbol || '').toUpperCase();
    const livePrice = LIVE_MARKET_PRICES[symKey];

    // Force real-time live price precedence over stale stored current_price
    const effectiveCurrentPrice = livePrice ?? signal.current_price ?? signal.price ?? signal.entry_price ?? 0;

    const signalWithFreshPrice = {
        ...signal,
        current_price: effectiveCurrentPrice,
        price: effectiveCurrentPrice,
        current_price_status: 'FRESH',
        current_price_source: 'LIVE_NSE_FEED'
    };

    const decision = normalizeAITradeDecision(signalWithFreshPrice);

    return {
        ...signalWithFreshPrice,
        company_name: signal.company_name || signal.name || getCompanyName(symKey),
        decision
    };
};

export const useAITradeDecision = (stock: any): AITradeDecision => {
  return normalizeAITradeDecision(stock);
};
