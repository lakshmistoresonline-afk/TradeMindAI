import json

with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
    data = json.load(f)

results = data['results']
corrected_results = []

wins = 0
losses = 0

for t in results:
    new_t = t.copy()
    if t['outcome'] == 'EXPIRED':
        new_t['outcome'] = 'STOP_LOSS'
        new_t['profit_pct'] = -3.0
        new_t['exit'] = t['stop']

    if new_t['outcome'] == 'TARGET_HIT':
        wins += 1
    elif new_t['outcome'] == 'STOP_LOSS':
        losses += 1

    corrected_results.append(new_t)

# Recalculate stats
total = len(corrected_results)
win_rate = (wins / total) * 100 if total > 0 else 0
avg_return = sum(t['profit_pct'] for t in corrected_results) / total if total > 0 else 0
total_return = sum(t['profit_pct'] for t in corrected_results)

# Calculate Max Drawdown (simple version for JSON stats)
cum_returns = 1.0
peak = 1.0
min_dd = 0.0
for t in corrected_results:
    cum_returns *= (1 + t['profit_pct']/100)
    if cum_returns > peak:
        peak = cum_returns
    dd = (cum_returns / peak - 1) * 100
    if dd < min_dd:
        min_dd = dd

output = {
    "metadata": data['metadata'],
    "stats": {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "unresolved": 0,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "total_return": total_return,
        "max_drawdown": min_dd
    },
    "results": corrected_results
}

with open('docs/STEP4_CORRECTED_RESULTS.json', 'w') as f:
    json.dump(output, f, indent=4)
print("Generated docs/STEP4_CORRECTED_RESULTS.json")
