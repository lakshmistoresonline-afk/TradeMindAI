const runCalcTests = () => {
  console.log('--- START: CALCULATION AUDIT ---');

  // Test Profit Factor
  const gains = [10, 20, 30];
  const losses = [-5, -15];
  const totalGains = gains.reduce((a, b) => a + b, 0);
  const totalLosses = Math.abs(losses.reduce((a, b) => a + b, 0));
  const profitFactor = totalLosses > 0 ? (totalGains / totalLosses).toFixed(2) : 'INF';
  console.log('Profit Factor (3.00 expected):', profitFactor === '3.00' ? 'PASS' : `FAIL: ${profitFactor}`);

  // Test Risk/Reward
  const entry = 100;
  const target = 120;
  const stop = 90;
  const rr = ((target - entry) / (entry - stop)).toFixed(2);
  console.log('Risk/Reward (2.00 expected):', rr === '2.00' ? 'PASS' : `FAIL: ${rr}`);

  // Test Market Bias (Simplified)
  const niftyChange = 0.8; // +0.8%
  const breadthRatio = 1.6; // Positive
  let score = 0;
  if (niftyChange > 0.5) score += 2;
  if (breadthRatio > 1.5) score += 2;
  const bias = score >= 3 ? 'STRONGLY BULLISH' : 'NEUTRAL';
  console.log('Market Bias (STRONGLY BULLISH expected):', bias === 'STRONGLY BULLISH' ? 'PASS' : `FAIL: ${bias}`);

  console.log('--- END: CALCULATION AUDIT ---');
};

runCalcTests();
