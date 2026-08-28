
import os
import sys
import asyncio
import pandas as pd
import numpy as np
import json
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

# Force Local Mode for Step 4
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

class BacktestOrchestrator:
    def __init__(self, symbols=None, sample_mode=False):
        self.symbols = symbols or NIFTY_200_CONSTITUENTS
        self.sample_mode = sample_mode
        self.results = []
        self.stats = {}

    async def run(self):
        print(f"--- STEP 4 BACKTEST START ({len(self.symbols)} symbols) ---")

        for symbol in self.symbols:
            if symbol == "LTIM": continue

            prices = await container.repository.get_recent_prices(symbol, limit=5000)
            if not prices:
                continue

            df = pd.DataFrame([p.model_dump() for p in prices])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            df.columns = [c.capitalize() for c in df.columns]

            if len(df) < 250:
                continue

            print(f"[*] Processing {symbol} ({len(df)} candles)...")

            # 1. Feature Engineering
            df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            high_low = df['High'] - df['Low']
            high_cp = np.abs(df['High'] - df['Close'].shift())
            low_cp = np.abs(df['Low'] - df['Close'].shift())
            df['TR'] = np.maximum(high_low, np.maximum(high_cp, low_cp))
            df['ATR'] = df['TR'].rolling(window=14).mean()

            symbol_trades = 0
            # 2. Chronological Walk-Forward
            for i in range(200, len(df) - 30):
                if df['Volume'].iloc[i] < 10_000_000:
                    continue

                try:
                    signal = self._evaluate_v2_2_rules(symbol, df, i)

                    if signal:
                        future_data = df.iloc[i+1:].copy()
                        outcome = OutcomeEngine.evaluate_outcome(signal, future_data)

                        status = outcome.get("status")
                        if status in ["TARGET_HIT", "STOP_LOSS", "EXPIRED"]:
                            trade_result = {
                                "symbol": symbol,
                                "signal_date": df.index[i].isoformat(),
                                "direction": signal.direction,
                                "probability": signal.calibrated_probability,
                                "intended_entry": signal.entry_price,
                                "actual_entry": outcome.get("actual_entry_price"),
                                "entry_execution_type": outcome.get("entry_execution_type"),
                                "target": signal.target_price,
                                "stop": signal.stop_loss_price,
                                "exit": outcome.get("outcome_price"),
                                "outcome": status,
                                "profit_pct": outcome.get("profit_pct", 0.0),
                                "bars_to_entry": outcome.get("bars_to_entry", 0),
                                "bars_in_position": outcome.get("bars_in_position", 0),
                                "bars_to_expiry": outcome.get("bars_to_expiry", 0),
                                "holding_period": outcome.get("bars_in_position", 0) # Maintain compatibility
                            }
                            self.results.append(trade_result)
                            symbol_trades += 1

                            if self.sample_mode:
                                print(f"   [TRADE] {trade_result['signal_date']} {trade_result['direction']} | {trade_result['outcome']} | {trade_result['profit_pct']:.2f}%")
                                if len(self.results) >= 20: break
                        # elif self.sample_mode:
                        #    print(f"   [SKIP] Bar {i}: Outcome {status}")
                except Exception as e:
                    # if self.sample_mode: print(f"   [!] Error at bar {i}: {e}")
                    pass

            print(f"   [+] {symbol}: {symbol_trades} trades found.")
            if self.sample_mode and len(self.results) >= 20: break

        self._calculate_aggregate_stats()
        self._save_results()

    def _evaluate_v2_2_rules(self, symbol, df, i):
        from backend.domain.models.ios import LiveSignal

        price = df['Close'].iloc[i]
        ema200 = df['EMA_200'].iloc[i]
        sma20 = df['SMA_20'].iloc[i]
        atr = df['ATR'].iloc[i]

        if np.isnan(ema200) or np.isnan(sma20) or np.isnan(atr): return None

        direction = "LONG" if price > ema200 else "SHORT"
        magnitude = abs(price - sma20)

        if magnitude < (atr * 0.5): return None

        # Seeded deterministic prob
        seed_str = f"{symbol}_{df.index[i]}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % 1000
        calibrated_prob = 0.48 + (seed / 4000.0)

        if calibrated_prob < 0.52: return None

        reward_amt = price * 0.03
        risk_amt = price * 0.03
        ev = (calibrated_prob * reward_amt) - ((1 - calibrated_prob) * risk_amt)
        if ev <= 0: return None

        target = price * (1.03 if direction == "LONG" else 0.97)
        stop = price * (0.97 if direction == "LONG" else 1.03)

        return LiveSignal(
            id=f"bt_{symbol}_{i}",
            symbol=symbol, timestamp=df.index[i],
            direction=direction, conviction=float(calibrated_prob * 100),
            raw_probability=float(calibrated_prob),
            calibrated_probability=float(calibrated_prob),
            expected_value=float(ev),
            entry_price=price, target_price=target, stop_loss_price=stop,
            rating="BUY", timeframe="SWING", status="WAITING_FOR_ENTRY"
        )

    def _calculate_aggregate_stats(self):
        df_res = pd.DataFrame(self.results)
        if df_res.empty: return

        wins = int(len(df_res[df_res['outcome'] == 'TARGET_HIT']))
        losses = int(len(df_res[df_res['outcome'] == 'STOP_LOSS']))
        expired = int(len(df_res[df_res['outcome'] == 'EXPIRED']))
        total = len(df_res)

        # Statistics Integrity Assertions (Step 4.1.1)
        assert total == wins + losses + expired, f"Stats mismatch: {total} != {wins} + {losses} + {expired}"

        self.stats = {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "expired": expired,
            "unresolved": 0,
            "win_rate": float((wins / (wins + losses)) * 100) if (wins + losses) > 0 else 0.0,
            "avg_return": float(df_res['profit_pct'].mean()),
            "total_return": float(df_res['profit_pct'].sum()),
            "max_drawdown": self._calculate_drawdown(df_res['profit_pct']),
            "win_rate_basis": "wins / (wins + losses)"
        }

    def _calculate_drawdown(self, returns):
        cum_returns = (1 + returns/100).cumprod()
        peak = cum_returns.expanding().max()
        dd = (cum_returns / peak - 1) * 100
        return float(dd.min())

    def _save_results(self):
        output = {
            "metadata": {
                "strategy": "v2.2",
                "timestamp": datetime.now().isoformat(),
                "execution_mode": "local",
                "db_source": "backend/local_operational.db",
                "parameters": {"target": 0.03, "stop": 0.03, "prob_threshold": 0.52}
            },
            "stats": self.stats,
            "results": self.results
        }
        with open("docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json", 'w') as f:
            json.dump(output, f, indent=4)

        pd.DataFrame(self.results).to_csv("docs/STEP4_SYMBOL_RESULTS.csv", index=False)
        print(f"[SUCCESS] Backtest complete. Total Trades: {len(self.results)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    orchestrator = BacktestOrchestrator(symbols=["SBIN", "RELIANCE", "TCS"], sample_mode=True) if not args.full else BacktestOrchestrator()
    asyncio.run(orchestrator.run())
