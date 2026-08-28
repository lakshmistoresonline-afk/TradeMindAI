import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
import yaml

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from scripts.accuracy.portfolio_simulator import PortfolioBacktestEngine

class RobustnessSuite:
    def __init__(self, config_path, results_path, db_path):
        self.config_path = config_path
        self.results_path = results_path
        self.db_path = db_path
        self.output_dir = Path("docs/step4_3")
        self.data_dir = Path("data/results/step4_3")

        with open(self.results_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        self.df_trades = pd.DataFrame(self.raw_data['results'])
        self.engine = PortfolioBacktestEngine(config_path, results_path, db_path)

    def run_probability_calibration(self):
        print("Running Probability Calibration...")
        df = self.df_trades.copy()
        buckets = [0.52, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 1.0]
        results = []
        for i in range(len(buckets)-1):
            low, high = buckets[i], buckets[i+1]
            subset = df[(df['probability'] >= low) & (df['probability'] < high)]
            if len(subset) == 0: continue

            wins = len(subset[subset['outcome'] == 'TARGET_HIT'])
            losses = len(subset[subset['outcome'] == 'STOP_LOSS'])
            wr = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0

            results.append({
                "bucket": f"{low}-{high}",
                "trades": len(subset),
                "win_rate": wr,
                "avg_return": subset['profit_pct'].mean(),
                "pnl": subset['profit_pct'].sum()
            })

        pd.DataFrame(results).to_csv(self.data_dir / "probability_buckets.csv", index=False)
        # Brier Score calculation
        df['y_true'] = (df['outcome'] == 'TARGET_HIT').astype(int)
        brier = ((df['probability'] - df['y_true'])**2).mean()

        with open(self.output_dir / "PROBABILITY_CALIBRATION.md", 'w') as f:
            f.write(f"# Step 4.3 Probability Calibration\n\n- Brier Score: {brier:.4f}\n\n" + pd.DataFrame(results).to_markdown())

    def run_threshold_sensitivity(self):
        print("Running Threshold Sensitivity...")
        thresholds = [0.52, 0.55, 0.58, 0.60, 0.62, 0.65, 0.70]
        results = []
        original_signals = self.engine.trades_data
        for t in thresholds:
            self.engine.trades_data = [s for s in original_signals if s['probability'] >= t]
            e_df, t_df = self.engine.run_simulation()
            final_equity = e_df['equity'].iloc[-1]
            results.append({
                "threshold": t,
                "trades": len(t_df),
                "return": (final_equity / 1000000 - 1) * 100,
                "win_rate": (len(t_df[t_df['pnl'] > 0]) / len(t_df)) * 100 if len(t_df) > 0 else 0
            })
        self.engine.trades_data = original_signals
        pd.DataFrame(results).to_csv(self.data_dir / "threshold_sensitivity.csv", index=False)

    def run_slippage_robustness(self):
        print("Running Slippage Robustness...")
        slips = [0.00, 0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0040, 0.0050]
        results = []
        for s in slips:
            e_df, t_df = self.engine.run_simulation(slippage_pct=s)
            final_equity = e_df['equity'].iloc[-1]
            results.append({
                "slippage_pct": s * 100,
                "return": (final_equity / 1000000 - 1) * 100,
                "drawdown": ((e_df['equity'] - e_df['equity'].cummax()) / e_df['equity'].cummax()).min() * 100
            })
        pd.DataFrame(results).to_csv(self.data_dir / "slippage_sensitivity.csv", index=False)
        with open(self.output_dir / "SLIPPAGE_ROBUSTNESS.md", 'w') as f:
            f.write("# Step 4.3 Slippage Robustness\n\n" + pd.DataFrame(results).to_markdown())

    def run_monte_carlo(self):
        print("Running Monte Carlo...")
        t_df = pd.read_csv("data/results/portfolio_trades.csv")
        returns = t_df['pnl'].tolist()
        num_sims = 10000
        results = []
        for _ in range(num_sims):
            shuffled = np.random.permutation(returns)
            equity = 1000000 + np.cumsum(shuffled)
            final_ret = (equity[-1] / 1000000 - 1) * 100
            peak = np.maximum.accumulate(equity)
            dd = ((equity - peak) / peak).min() * 100
            results.append({"final_return": final_ret, "max_drawdown": dd})

        mc_df = pd.DataFrame(results)
        mc_df.to_csv(self.data_dir / "monte_carlo_results.csv", index=False)

        stats = {
            "5th": mc_df.quantile(0.05).to_dict(),
            "median": mc_df.quantile(0.50).to_dict(),
            "95th": mc_df.quantile(0.95).to_dict()
        }
        with open(self.output_dir / "MONTE_CARLO_REPORT.md", 'w') as f:
            f.write("# Step 4.3 Monte Carlo Report\n\n" + pd.DataFrame(stats).to_markdown())

    def run_all(self):
        self.run_probability_calibration()
        self.run_threshold_sensitivity()
        self.run_slippage_robustness()
        self.run_monte_carlo()

if __name__ == "__main__":
    suite = RobustnessSuite("config/portfolio_backtest.yaml", "docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json", "backend/local_operational.db")
    suite.run_all()
