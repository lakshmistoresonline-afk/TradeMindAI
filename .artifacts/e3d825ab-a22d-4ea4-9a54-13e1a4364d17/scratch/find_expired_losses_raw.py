import json

with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
    data = json.load(f)

expired_trades = [t for t in data['results'] if t['outcome'] == 'EXPIRED']

anomalies = []
for t in expired_trades:
    entry = t['entry']
    exit_price = t['exit']
    direction = t['direction']

    if direction == 'LONG':
        raw_profit_pct = ((exit_price - entry) / entry) * 100
    else:
        raw_profit_pct = ((entry - exit_price) / entry) * 100

    if raw_profit_pct < -5:
        t['raw_profit_pct'] = raw_profit_pct
        anomalies.append(t)

print(f"Total EXPIRED trades: {len(expired_trades)}")
print(f"EXPIRED trades with RAW profit_pct < -5%: {len(anomalies)}")

for t in anomalies[:10]:
    print(json.dumps(t, indent=2))
