import { validateMetric, MetricRegistry } from './metrics';

const runTests = () => {
  console.log('--- START: METRIC REGISTRY AUDIT ---');

  // Test Price
  const priceTest = validateMetric('price', 2500);
  console.log('Price Valid:', priceTest.isValid ? 'PASS' : 'FAIL');

  const priceInvalid = validateMetric('price', -10);
  console.log('Price Invalid Check:', !priceInvalid.isValid ? 'PASS' : 'FAIL');

  // Test Conviction
  const convTest = validateMetric('conviction', 85);
  console.log('Conviction Valid:', convTest.isValid ? 'PASS' : 'FAIL');

  const convOOB = validateMetric('conviction', 120);
  console.log('Conviction OOB Check:', !convOOB.isValid ? 'PASS' : 'FAIL');

  // Test Formatter
  const priceFormatter = MetricRegistry['price'].formatter!(1234.5);
  console.log('Price Formatter:', priceFormatter === '₹1,234.5' ? 'PASS' : `FAIL: ${priceFormatter}`);

  const convFormatter = MetricRegistry['conviction'].formatter!(85.6);
  console.log('Conviction Formatter:', convFormatter === '86%' ? 'PASS' : `FAIL: ${convFormatter}`);

  console.log('--- END: METRIC REGISTRY AUDIT ---');
};

runTests();
