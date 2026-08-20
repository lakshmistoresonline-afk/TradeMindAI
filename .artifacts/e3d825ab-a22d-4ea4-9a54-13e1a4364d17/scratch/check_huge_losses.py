import json
with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
    data = json.load(f)
results = data['results']
huge = [t for t in results if t['profit_pct'] < -10]
print(f"Trades with profit_pct < -10%: {len(huge)}")
for t in huge[:10]:
    print(t)
