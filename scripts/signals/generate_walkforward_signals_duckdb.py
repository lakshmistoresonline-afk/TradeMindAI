"""
================================================================================
TradeMindAI: Time-Safe DuckDB Walk-Forward Signal Engine (v3.6-ATOMIC-EXPORT)
================================================================================
1. Connects to live DuckDB database (`backend/data/analytical.duckdb`).
2. Iterates chronologically day-by-day across all Nifty 500 equities.
3. Evaluates Donchian breakouts, EMA alignment, and Wilder's RSI (14) for zero-lookahead BUY setups.
4. Dynamically calculates conviction_score from technical driver metrics (replacing hardcoded values).
5. Uses authoritative evaluate_horizon_outcome() with conservative same-bar stop-loss resolution.
6. Right-Censoring Correction: Incomplete forward horizons with len(future_sub) < horizon
   that touch neither target nor stop are explicitly classified as INCOMPLETE_WINDOW and
   excluded from completed-trade win rate and PnL summary metrics.
7. Evaluates forward price movement across 5, 10, 20, and 60 session horizons.
8. Safely builds and writes export payload via atomic file replacement with allow_nan=False.
================================================================================
"""

import os
import sys
import json
import duckdb
import tempfile
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.services.indicator_service import compute_wilder_rsi
from backend.app.services.horizon_engine import evaluate_horizon_outcome

duckdb_path = root_dir / "backend" / "data" / "analytical.duckdb"
signals_json_path = root_dir / "backend" / "data" / "signals_history.json"

def calculate_conviction_score(rsi: float, price: float, ema20: float, ema50: float, donchian_high: float, volume_relative: float) -> float:
    """
    Calculates a dynamic, non-probabilistic technical conviction score in [50.0, 95.0].
    """
    base_score = 65.0

    # RSI Momentum Factor
    if 50.0 <= rsi <= 65.0:
        base_score += 10.0
    elif 65.0 < rsi <= 75.0:
        base_score += 5.0

    # EMA Alignment Factor
    if price > ema20 > ema50:
        base_score += 10.0

    # Donchian Breakout Clearance Factor
    if donchian_high > 0 and price >= donchian_high:
        clearance_pct = ((price - donchian_high) / donchian_high) * 100
        base_score += min(clearance_pct * 2.0, 10.0)

    return round(min(max(base_score, 50.0), 95.0), 1)

def build_export_payload(
    active_buy_signals: list,
    all_history_signals: list,
    total_candidates: int,
    source_tag: str = "DUCKDB_WALKFORWARD_ENGINE_v3.6_ATOMIC_EXPORT"
) -> dict:
    """
    Builds the production export JSON payload ensuring:
    - Booleans remain native Python bool (serializing as JSON true/false)
    - Safe conversion of pandas/NumPy scalars to native Python types
    - No invalid JSON tokens (NaN / Infinity) emitted
    - Capped history records (top 25,000) preserving export schema compatibility
    - Explicit separation of completed trades vs incomplete windows
    """
    def sanitize_val(v):
        if isinstance(v, (bool, np.bool_)):
            return bool(v)
        if v is None or v is pd.NaT:
            return None
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        if isinstance(v, (float, np.floating)):
            if np.isnan(v) or np.isinf(v):
                return None
            return float(v)
        if isinstance(v, (int, np.integer)):
            return int(v)
        if isinstance(v, (datetime, pd.Timestamp)):
            return v.isoformat()
        return str(v)

    clean_active = []
    for sig in active_buy_signals:
        clean_active.append({k: sanitize_val(v) for k, v in sig.items()})

    clean_history = []
    for sig in all_history_signals[:25000]: # Cap top 25,000 for JSON file size contract
        clean_history.append({k: sanitize_val(v) for k, v in sig.items()})

    return {
        "active_signals": clean_active,
        "history_records": clean_history,
        "summary": {
            "total_candidates": int(total_candidates),
            "total_evaluations": len(all_history_signals),
            "active_buy_count": len(clean_active)
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source_tag
    }

def write_export_payload(payload: dict, output_path: Path = None) -> Path:
    """
    Safely writes export payload using atomic temporary-file replacement.
    Ensures serialization with allow_nan=False succeeds before overwriting target.
    Unlinks temporary file if serialization or writing fails.
    """
    target_path = Path(output_path) if output_path else signals_json_path
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    temp_file = None
    try:
        # Test serialization first with allow_nan=False inside try block
        json_bytes = json.dumps(payload, indent=2, allow_nan=False).encode("utf-8")

        fd, temp_file = tempfile.mkstemp(dir=str(target_dir), suffix=".json")
        with os.fdopen(fd, "wb") as f:
            f.write(json_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, str(target_path))
    except Exception as ex:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass
        raise RuntimeError(f"Failed atomic write for export payload to '{target_path}': {ex}") from ex

    return target_path

def run_duckdb_signal_engine():
    print("================================================================================")
    print("  TRADEMIND AI: DUCKDB TIME-SAFE WALK-FORWARD SIGNAL ENGINE (v3.6 ATOMIC EXPORT)")
    print("================================================================================\n")

    if not duckdb_path.exists():
        raise RuntimeError(f"DuckDB database missing at '{duckdb_path}'. Ingestion required first.")

    con = duckdb.connect(str(duckdb_path), read_only=True)
    symbols = [r[0] for r in con.execute("SELECT DISTINCT symbol FROM daily_ohlcv ORDER BY symbol").fetchall()]
    print(f"[*] Loaded {len(symbols)} distinct symbols from DuckDB `daily_ohlcv` table.")

    all_history_signals = []
    active_buy_signals = []

    horizons = [5, 10, 20, 60]
    total_scanned_bars = 0
    total_candidates = 0

    for idx, sym in enumerate(symbols, 1):
        df_sym = con.execute("""
            SELECT symbol, date, open as Open, high as High, low as Low, close as Close, volume as Volume
            FROM daily_ohlcv WHERE symbol = ?
            ORDER BY date
        """, [sym]).df()

        if len(df_sym) < 30:
            continue

        total_scanned_bars += len(df_sym)

        # Compute Technical Indicators with Wilder RSI (14)
        df_sym["date"] = pd.to_datetime(df_sym["date"]).dt.strftime("%Y-%m-%d")
        df_sym["ema_20"] = df_sym["Close"].ewm(span=20, adjust=False).mean()
        df_sym["ema_50"] = df_sym["Close"].ewm(span=50, adjust=False).mean()
        df_sym["ema_200"] = df_sym["Close"].ewm(span=200, adjust=False).mean()
        df_sym["rsi_14"] = compute_wilder_rsi(df_sym["Close"], period=14)

        # 20-period Donchian High (shifted 1 bar for zero lookahead)
        df_sym["donchian_high_20"] = df_sym["High"].shift(1).rolling(window=20).max()

        # Walk forward through trading bars
        for i in range(30, len(df_sym)):
            r = df_sym.iloc[i]
            entry_dt = str(r["date"])
            entry_p = float(r["Close"])
            volume = float(r["Volume"])

            # Filter non-positive or ultra-illiquid penny stock noise
            if entry_p < 5.0 or volume < 1000:
                continue

            ema20 = float(r["ema_20"])
            ema50 = float(r["ema_50"])
            rsi = float(r["rsi_14"])
            donchian_h = r["donchian_high_20"]

            # Strategy Trigger: Price >= 20-bar Donchian High & Price > 20 EMA & 20 EMA > 50 EMA & RSI in [45, 75]
            if pd.isna(donchian_h) or entry_p < donchian_h:
                continue
            if pd.isna(rsi) or rsi < 45.0 or rsi > 75.0:
                continue
            if entry_p < ema20 or ema20 < ema50:
                continue

            total_candidates += 1

            # Candidate Signal Geometry
            target_p = round(entry_p * 1.08, 2)
            stop_p = round(entry_p * 0.95, 2)
            conviction_score = calculate_conviction_score(rsi, entry_p, ema20, ema50, donchian_h, volume)

            # Evaluate forward horizons using Authoritative evaluate_horizon_outcome()
            for horizon in horizons:
                future_sub = df_sym.iloc[i+1 : i+1+horizon]
                outcome = evaluate_horizon_outcome(entry_p, target_p, stop_p, future_sub, horizon)

                if outcome["status"] == "ACTIVE":
                    if horizon == 20: # Use 20-day horizon for primary active display
                        active_buy_signals.append({
                            "id": f"sig_{sym}_{entry_dt}",
                            "symbol": sym,
                            "direction": "BUY",
                            "timeframe": "DAILY",
                            "horizon_days": horizon,
                            "entry_price": entry_p,
                            "target_price": target_p,
                            "stop_price": stop_p,
                            "rsi_14": round(rsi, 1),
                            "timestamp": entry_dt,
                            "status": "ACTIVE",
                            "conviction_score": conviction_score
                        })
                    continue

                all_history_signals.append({
                    "id": f"hist_{sym}_{entry_dt}_h{horizon}",
                    "symbol": sym,
                    "direction": "BUY",
                    "horizon_days": horizon,
                    "entry_date": entry_dt,
                    "entry_price": entry_p,
                    "target_price": target_p,
                    "stop_price": stop_p,
                    "exit_date": outcome["exit_date"],
                    "exit_price": outcome["exit_price"],
                    "status": outcome["status"],
                    "pnl_pct": outcome["pnl_pct"],
                    "conviction_score": conviction_score,
                    "is_full_horizon": outcome["is_full_horizon"]
                })

    con.close()

    print(f"\n[+] Scanned {total_scanned_bars} price bars across {len(symbols)} symbols.")
    print(f"[+] Total BUY Candidates Generated: {total_candidates}")
    print(f"[+] Total Historical Horizon Evaluated Trades: {len(all_history_signals)}")
    print(f"[+] Total Active Current BUY Setups: {len(active_buy_signals)}")

    # Calculate Win Rates strictly across COMPLETED / FULL HORIZON Trades
    df_hist = pd.DataFrame(all_history_signals)
    if not df_hist.empty:
        for h in horizons:
            sub_h = df_hist[(df_hist["horizon_days"] == h) & (df_hist["status"] != "INCOMPLETE_WINDOW")]
            incomplete_cnt = (df_hist[(df_hist["horizon_days"] == h)]["status"] == "INCOMPLETE_WINDOW").sum()
            if not sub_h.empty:
                hits = (sub_h["status"] == "TARGET_HIT").sum()
                stops = (sub_h["status"] == "STOP_LOSS").sum()
                exp = (sub_h["status"] == "EXPIRED").sum()
                win_rate = round((hits / len(sub_h)) * 100, 2)
                avg_pnl = round(sub_h["pnl_pct"].mean(), 2)
                print(f"   * Horizon {h:2d} Days: CompletedTrades={len(sub_h):5d}, IncompleteWindow={incomplete_cnt:3d}, TargetHit={hits:5d}, StopLoss={stops:5d}, Expired={exp:5d}, WinRate={win_rate:5.2f}%, AvgPnL={avg_pnl:5.2f}%")

    # Safely write export payload via atomic file replacement
    payload = build_export_payload(active_buy_signals, all_history_signals, total_candidates)
    out_path = write_export_payload(payload)
    print(f"\n[+] Exported signals history & active signals to '{out_path}'")

if __name__ == "__main__":
    run_duckdb_signal_engine()
