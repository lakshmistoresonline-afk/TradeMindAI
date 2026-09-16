import pandas as pd
import numpy as np
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

def calculate():
    df = pd.read_csv("historical_signals.csv")

    # 1. Performance Metrics
    trade_count = len(df)
    wins = len(df[df['status'] == 'TARGET_HIT'])
    losses = len(df[df['status'] == 'STOP_LOSS'])
    win_rate = (wins / trade_count) * 100

    gross_profit = df[df['net_pnl'] > 0]['net_pnl'].sum()
    gross_loss = abs(df[df['net_pnl'] < 0]['net_pnl'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    expectancy = df['net_pnl'].mean()
    net_pnl = df['net_pnl'].sum()

    # 2. Probability Validation
    # Map status to binary outcome (TARGET_HIT = 1, STOP_LOSS = 0)
    df['outcome_binary'] = df['status'].apply(lambda x: 1 if x == 'TARGET_HIT' else 0)

    # Calibration metrics
    y_true = df['outcome_binary'].values
    y_prob = df['calibrated_probability'].values

    brier = brier_score_loss(y_true, y_prob)
    ll = log_loss(y_true, y_prob)
    try:
        auc = roc_auc_score(y_true, y_prob)
    except:
        auc = 0.5

    print(f"Sample Size: {trade_count}")
    print(f"Wins: {wins}, Losses: {losses}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Expectancy: {expectancy:.4f}")
    print(f"Net P&L: {net_pnl:.2f}")
    print(f"Brier Score: {brier:.4f}")
    print(f"Log Loss: {ll:.4f}")
    print(f"ROC-AUC: {auc:.4f}")

    # 3. Drawdown (Simplified)
    equity_curve = df['net_pnl'].cumsum()
    max_equity = equity_curve.expanding().max()
    drawdown = (equity_curve - max_equity)
    max_drawdown = drawdown.min()
    print(f"Max Drawdown: {max_drawdown:.2f}")

    # 4. Regime Analysis
    if 'regime' in df.columns:
        print("\n--- PERFORMANCE BY REGIME ---")
        regime_stats = df.groupby('regime')['net_pnl'].agg(['count', 'mean', 'sum'])
        print(regime_stats.to_markdown())

    # 5. Direction Analysis
    print("\n--- PERFORMANCE BY DIRECTION ---")
    direction_stats = df.groupby('direction')['net_pnl'].agg(['count', 'mean', 'sum'])
    print(direction_stats.to_markdown())

if __name__ == "__main__":
    calculate()
