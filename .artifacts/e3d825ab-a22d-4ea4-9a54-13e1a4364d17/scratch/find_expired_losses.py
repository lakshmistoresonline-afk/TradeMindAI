import json

with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
    data = json.load(f)

expired_trades = [t for t in data['results'] if t['outcome'] == 'EXPIRED']
print(f"Total EXPIRED trades: {len(expired_trades)}")

losses = [t for t in expired_trades if t['profit_pct'] < -5]
print(f"EXPIRED trades with profit_pct < -5%: {len(losses)}")

for t in losses[:10]:
    print(t)
