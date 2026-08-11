import { normalizeAITradeDecision } from './useAITradeDecision';

const mockStock = {
  symbol: 'RELIANCE',
  last_price: 2500,
  ai_investment_score: 85,
  beta: 1.1,
  updated_at: '2026-08-09T10:00:00Z',
  structured_consensus: {
    rating: 'STRONG BUY',
    conviction: 88,
    timeframe: 'MID_TERM',
    entryZone: { low: 2450, high: 2480 },
    target: 2800,
    stop_loss: 2350,
    thesis: 'Strong breakout'
  }
};

const decision = normalizeAITradeDecision(mockStock);

console.log('--- TEST: Normalization ---');
console.log('Rating:', decision.rating === 'STRONG BUY' ? 'PASS' : `FAIL: ${decision.rating}`);
console.log('Conviction:', decision.conviction === 88 ? 'PASS' : `FAIL: ${decision.conviction}`);
console.log('Timeframe:', decision.timeframe === 'POSITION' ? 'PASS' : `FAIL: ${decision.timeframe}`);
console.log('EntryZone:', decision.entryLow === 2450 ? 'PASS' : `FAIL: ${decision.entryLow}`);
console.log('--- END TEST ---');
