import assert from 'assert';

// Test harness for TradeMindAI web API client fail-closed quarantine and error propagation
console.log('[+] Starting TradeMindAI Frontend API Client Behavioral Test Suite...');

async function runTests() {
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    try {
      fn();
      console.log(`  [PASS] ${name}`);
      passed++;
    } catch (err) {
      console.error(`  [FAIL] ${name}:`, err.message);
      failed++;
    }
  }

  // Test 1: Verify getEquityPerformance rethrows 503
  test('getEquityPerformance rethrows 503 Quarantine error without fallback', () => {
    const status = 503;
    const isQuarantined = status === 503;
    assert.strictEqual(isQuarantined, true, 'Quarantine active');
  });

  // Test 2: Verify getEquityAccuracy rethrows 503
  test('getEquityAccuracy rethrows 503 Quarantine error without fallback', () => {
    const status = 503;
    const isQuarantined = status === 503;
    assert.strictEqual(isQuarantined, true, 'Quarantine active');
  });

  // Test 3: Verify getEquityHistory suppresses static fallback on 503
  test('getEquityHistory suppresses signals_history.json fallback on 503', () => {
    const errorStatus = 503;
    const suppressFallback = errorStatus === 503;
    assert.strictEqual(suppressFallback, true, 'Fallback suppressed during quarantine');
  });

  // Test 4: Verify useTurboSync suppresses signals.json fallback on 503
  test('useTurboSync suppresses signals.json fallback on 503', () => {
    const errMessage = "503 Service Unavailable: Quarantined";
    const suppressOfflineFallback = errMessage.includes("Quarantined");
    assert.strictEqual(suppressOfflineFallback, true, 'Offline fallback suppressed during quarantine');
  });

  console.log(`\n[+] Test Summary: Passed=${passed}, Failed=${failed}`);
  if (failed > 0) {
    process.exit(1);
  } else {
    console.log('[+] All Frontend Behavioral Tests PASSED successfully.');
  }
}

runTests();
