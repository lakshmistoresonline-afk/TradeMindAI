"""
================================================================================
TradeMindAI: Research-Only Technical Features Calculator (v2.3-RESEARCH)
================================================================================
Implements candidate research features (Trend/Regime, Volatility, Volume, Price Structure)
strictly for out-of-sample evaluation. Enforces strict causal point-in-time integrity,
shifted Donchian levels, feature-specific history readiness, and rigorous OHLCV/benchmark data contracts.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

class ResearchFeatures:
    """
    Feature Readability & Lookback Requirements:
    - EMA / SMA / RSI / ATR / MACD: 14 to 50 bars warm-up.
    - Donchian 20-bar: 21 bars (20 + 1 shift for zero look-ahead).
    - Donchian 55-bar: 56 bars (55 + 1 shift for zero look-ahead).
    - Relative Strength (20, 60, 120 days): 20, 60, 120 bars respectively.
    - Rolling Percentiles (ATR, Bollinger Bandwidth 252-row window): 252 bars.
    """

    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        """
        Enforces strict data contracts on input OHLCV dataframe.
        Does not mutate the caller's DataFrame. Normalizes column names (case-insensitive, whitespace-trimmed),
        rejects duplicate columns, validates timestamps and geometry.
        """
        if df is None or df.empty:
            raise ValueError("Input DataFrame is empty or None.")

        # Do not mutate caller's df
        df_norm = df.copy()

        # Normalize column names by stripping whitespace and capitalizing
        cols = [str(c).strip() for c in df_norm.columns]
        normalized_cols = [c.capitalize() for c in cols]
        df_norm.columns = normalized_cols

        if len(normalized_cols) != len(set(normalized_cols)):
            raise ValueError(f"Duplicate columns detected after normalization: {list(df.columns)}")

        required = ["Open", "High", "Low", "Close", "Volume"]
        for col in required:
            if col not in df_norm.columns:
                raise ValueError(f"Missing required OHLCV column: {col}. Available: {list(df_norm.columns)}")

        # Check index is datetime and monotonic/unique
        if not isinstance(df_norm.index, pd.DatetimeIndex):
            try:
                df_norm.index = pd.to_datetime(df_norm.index)
            except Exception as e:
                raise ValueError(f"DataFrame index cannot be parsed as DatetimeIndex: {e}") from e

        if not df_norm.index.is_monotonic_increasing:
            raise ValueError("DataFrame index timestamps are not monotonically increasing.")

        if df_norm.index.duplicated().any():
            raise ValueError("Duplicate timestamps detected in DataFrame index.")

        # Check finite and positive prices
        price_cols = ["Open", "High", "Low", "Close"]
        for col in price_cols:
            s = pd.to_numeric(df_norm[col], errors='coerce')
            if s.isna().any() or not np.isfinite(s).all() or (s <= 0).any():
                raise ValueError(f"Column {col} contains non-finite, non-positive, or missing values.")
            df_norm[col] = s

        # Check non-negative volume
        v = pd.to_numeric(df_norm["Volume"], errors='coerce')
        if v.isna().any() or not np.isfinite(v).all() or (v < 0).any():
            raise ValueError("Volume contains non-finite, negative, or missing values.")
        df_norm["Volume"] = v

        # Check OHLC geometric relationships
        if ((df_norm["Low"] > df_norm["Open"]) | (df_norm["Low"] > df_norm["Close"]) |
            (df_norm["High"] < df_norm["Open"]) | (df_norm["High"] < df_norm["Close"]) |
            (df_norm["High"] < df_norm["Low"])).any():
            raise ValueError("Invalid OHLC geometry detected (Low > Open/Close or High < Open/Close/Low).")

        return df_norm

    @staticmethod
    def calculate_research_features(df: pd.DataFrame, benchmark_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Calculates extended research technical features using completed historical candles only.
        Guarantees point-in-time integrity and zero look-ahead bias by shifting structural levels by 1 bar.
        Features that have insufficient history return NaN without rejecting the entire calculation.
        """
        df_clean = ResearchFeatures.validate_ohlcv(df)

        if len(df_clean) < 55:
            raise ValueError(f"Insufficient history for research features. Required at least 55 rows, got {len(df_clean)}.")

        df_out = df_clean.copy()

        try:
            import pandas_ta as pta

            # 1. Trend & Regime Features
            df_out["res_ema_5"] = pta.ema(df_out["Close"], length=5)
            df_out["res_ema_10"] = pta.ema(df_out["Close"], length=10)
            df_out["res_ema_slope_5"] = df_out["res_ema_5"].diff(5) / 5.0
            df_out["res_ema_slope_10"] = df_out["res_ema_10"].diff(10) / 10.0

            adx = pta.adx(df_out["High"], df_out["Low"], df_out["Close"], length=14)
            if adx is not None:
                df_out["res_adx_14"] = adx.iloc[:, 0]
                df_out["res_adx_regime_20"] = (df_out["res_adx_14"] > 20.0).astype(float)
                df_out["res_adx_regime_25"] = (df_out["res_adx_14"] > 25.0).astype(float)

            # 2. Volatility & Risk Features
            df_out["res_atr_14"] = pta.atr(df_out["High"], df_out["Low"], df_out["Close"], length=14)
            df_out["res_natr"] = (df_out["res_atr_14"] / df_out["Close"]) * 100.0

            # ATR percentile over 252 rolling window (respects readiness readiness boundary)
            rolling_atr = df_out["res_atr_14"].rolling(window=252, min_periods=252)
            df_out["res_atr_percentile"] = rolling_atr.apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) == 252 else np.nan, raw=False)

            bbands = pta.bbands(df_out["Close"], length=20, std=2.0)
            if bbands is not None:
                bb_width = (bbands.iloc[:, 2] - bbands.iloc[:, 0]) / bbands.iloc[:, 1]
                rolling_bw = bb_width.rolling(window=252, min_periods=252)
                df_out["res_bb_bandwidth_pct"] = rolling_bw.apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) == 252 else np.nan, raw=False)

            # 3. Volume Confirmation Features
            vol_sma_20 = pta.sma(df_out["Volume"], length=20)
            vol_sma_50 = pta.sma(df_out["Volume"], length=50)
            df_out["res_rel_vol_20"] = df_out["Volume"] / (vol_sma_20 + 1e-9)
            df_out["res_rel_vol_50"] = df_out["Volume"] / (vol_sma_50 + 1e-9)

            obv = pta.obv(df_out["Close"], df_out["Volume"])
            df_out["res_obv_slope_5"] = obv.diff(5)
            df_out["res_mfi_14"] = pta.mfi(df_out["High"], df_out["Low"], df_out["Close"], df_out["Volume"], length=14)

            # 4. Price Structure Features (Causality: Shifted by 1 bar to use prior completed bars only)
            df_out["res_donchian_high_20"] = df_out["High"].rolling(window=20).max().shift(1)
            df_out["res_donchian_low_20"] = df_out["Low"].rolling(window=20).min().shift(1)
            df_out["res_donchian_high_55"] = df_out["High"].rolling(window=55).max().shift(1)
            df_out["res_donchian_low_55"] = df_out["Low"].rolling(window=55).min().shift(1)

            # 5. Relative Strength vs Benchmark (20, 60, 120 days) - normalized via validate_ohlcv, no silent zeroing, returns NaN if missing/misaligned
            if benchmark_df is not None and not benchmark_df.empty:
                try:
                    bench_clean = ResearchFeatures.validate_ohlcv(benchmark_df)
                    bench_close = bench_clean["Close"].reindex(df_out.index, method=None) # Strict alignment, no forward fill staleness

                    stock_ret_20 = df_out["Close"].pct_change(20)
                    bench_ret_20 = bench_close.pct_change(20)
                    df_out["res_rs_20d"] = stock_ret_20 - bench_ret_20

                    stock_ret_60 = df_out["Close"].pct_change(60)
                    bench_ret_60 = bench_close.pct_change(60)
                    df_out["res_rs_60d"] = stock_ret_60 - bench_ret_60

                    stock_ret_120 = df_out["Close"].pct_change(120)
                    bench_ret_120 = bench_close.pct_change(120)
                    df_out["res_rs_120d"] = stock_ret_120 - bench_ret_120
                except Exception:
                    df_out["res_rs_20d"] = np.nan
                    df_out["res_rs_60d"] = np.nan
                    df_out["res_rs_120d"] = np.nan
            else:
                df_out["res_rs_20d"] = np.nan
                df_out["res_rs_60d"] = np.nan
                df_out["res_rs_120d"] = np.nan

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise RuntimeError(f"[ResearchFeatures] Error calculating research features: {e}") from e

        return df_out
