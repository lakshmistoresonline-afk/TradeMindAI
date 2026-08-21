import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def forensic_audit():
    print("--- TRADEMIND AI STEP 4.4.3 FORENSIC AUDIT ---")

    # 1. Step 4.2 Reconciliation
    print("[*] Auditing Step 4.2 Trade Count...")
    s42_results_path = "docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json"
    s42_trades_path = "data/results/portfolio_trades.csv"

    with open(s42_results_path, 'r') as f:
        s42_signals = json.load(f)['results']
    s42_executed = pd.read_csv(s42_trades_path)

    print(f"   Raw Signals Count: {len(s42_signals)}")
    print(f"   Executed Trades Count: {len(s42_executed)}")

    # 2. Step 4.4.2 Reconciliation
    print("[*] Auditing Step 4.4.2 Canonical Ledger...")
    wf_trades_path = "data/results/step4_4_2/wf_portfolio_trades.csv"
    wf_equity_path = "data/results/step4_4_2/wf_portfolio_equity.csv"

    t_df = pd.read_csv(wf_trades_path)
    e_df = pd.read_csv(wf_equity_path)

    total_trades = len(t_df)
    unique_ids = t_df['trade_id'].nunique()
    unique_logic = t_df.groupby(['symbol', 'signal_date', 'direction']).ngroups

    print(f"   Total Trades: {total_trades}")
    print(f"   Unique IDs: {unique_ids}")
    print(f"   Unique Signal Logic: {unique_logic}")

    # 3. Final Equity Verification
    starting_cap = 1000000.0
    sum_pnl = t_df['pnl'].sum()
    reported_final = e_df['equity'].iloc[-1]

    print(f"   Starting Capital: {starting_cap:,.2f}")
    print(f"   Sum PnL: {sum_pnl:,.2f}")
    print(f"   Start + Sum PnL: {starting_cap + sum_pnl:,.2f}")
    print(f"   Reported Final Equity: {reported_final:,.2f}")
    print(f"   Discrepancy: {abs(starting_cap + sum_pnl - reported_final):.6f}")

    # 4. Slippage Forensic
    print("[*] Auditing Slippage Application...")
    # Calculate volume per trade
    t_df['volume'] = t_df['quantity'] * t_df['actual_entry'] + t_df['quantity'] * t_df['exit_price']
    total_volume = t_df['volume'].sum()
    print(f"   Total Traded Volume: {total_volume:,.2f}")

    # Base Costs verification
    print("[*] Auditing Transaction Costs...")
    # Production Model: STT(0.1%), Exchange(0.00345%), GST(18% of broker+exch), SEBI(0.0001%), Stamp(0.015%)
    # Let's check a sample trade
    sample = t_df.iloc[0]
    val_entry = sample['quantity'] * sample['actual_entry']
    val_exit = sample['quantity'] * sample['exit_price']

    # Simple estimate of STT (0.1% on both sides for delivery)
    stt_est = (val_entry + val_exit) * 0.001
    print(f"   Sample {sample['symbol']} Total Value: {val_entry + val_exit:,.2f}")
    print(f"   Sample STT Estimate: {stt_est:,.2f}")
    print(f"   Sample Total Cost Reported: {sample['transaction_cost']:,.2f}")

    # 5. Universe Audit
    print("[*] Auditing NIFTY 200 Universe...")
    from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
    symbols_in_backtest = t_df['symbol'].unique()
    missing = set(NIFTY_200_CONSTITUENTS) - set(symbols_in_backtest)
    print(f"   Configured: {len(NIFTY_200_CONSTITUENTS)}")
    print(f"   Symbols Traded: {len(symbols_in_backtest)}")
    print(f"   Missing (No Trades): {len(missing)}")

if __name__ == "__main__":
    forensic_audit()
