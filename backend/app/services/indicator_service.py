"""
================================================================================
TradeMindAI: Local Indicator Service (v3.0-CANONICAL-PERIOD-POLICY)
================================================================================
Computes technical analysis metrics locally across historical price candles:
RSI (14 Wilder Exponential Smoothing), MACD (12, 26, 9), EMA (20, 50, 100, 200),
SMA (20, 50, 200), Bollinger Bands (20, 2), ATR (14), and Shifted Donchian Channels (20).
Enforces case-insensitive column normalization, strict warm-up policies,
and point-in-time causality without fabricated constant fallbacks.
================================================================================
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

def compute_wilder_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Computes Wilder's Exponentially Smoothed RSI (14) with robust handling for:
    - Positive gain, zero loss -> 100.0
    - Zero gain, positive loss -> 0.0
    - Zero gain, zero loss -> 50.0 (neutral-flat)
    - Warm-up period (first `period` valid contiguous bars) -> NaN
    - Internal NaN / missing prices -> handled gracefully with contiguous reset requirement
    - Period type validation -> accepts Python int and NumPy integer scalars, rejects bool, float, str, <= 0
    """
    if isinstance(period, (bool, np.bool_)) or not isinstance(period, (int, np.integer)) or period <= 0:
        raise ValueError(f"RSI period must be a positive integer, got {period}")

    period = int(period)

    if series is None or series.empty or len(series) <= period:
        idx = series.index if series is not None and hasattr(series, "index") else None
        return pd.Series(np.nan, index=idx)

    # Convert to numeric float Series replacing infinities with NaN
    s_clean = pd.to_numeric(series, errors="coerce").astype(float)
    s_clean = s_clean.replace([np.inf, -np.inf], np.nan)

    delta = s_clean.diff()
    gain_series = delta.clip(lower=0.0)
    loss_series = (-delta).clip(lower=0.0)

    n = len(s_clean)
    avg_gain = np.full(n, np.nan)
    avg_loss = np.full(n, np.nan)

    # Track contiguous valid deltas
    contiguous_valid = 0

    for i in range(1, n):
        g = gain_series.iloc[i]
        l = loss_series.iloc[i]

        if np.isnan(g) or np.isnan(l):
            contiguous_valid = 0
            avg_gain[i] = np.nan
            avg_loss[i] = np.nan
        else:
            contiguous_valid += 1
            if contiguous_valid < period:
                avg_gain[i] = np.nan
                avg_loss[i] = np.nan
            elif contiguous_valid == period:
                # Initial SMA over period valid contiguous deltas
                start_bar = i - period + 1
                avg_gain[i] = gain_series.iloc[start_bar : i + 1].mean()
                avg_loss[i] = loss_series.iloc[start_bar : i + 1].mean()
            else:
                # Wilder Exponential Smoothing
                avg_gain[i] = (avg_gain[i - 1] * (period - 1) + g) / period
                avg_loss[i] = (avg_loss[i - 1] * (period - 1) + l) / period

    rsi = np.full(n, np.nan)
    for i in range(n):
        g = avg_gain[i]
        l = avg_loss[i]
        if np.isnan(g) or np.isnan(l):
            rsi[i] = np.nan
        elif l == 0.0 and g > 0.0:
            rsi[i] = 100.0
        elif g == 0.0 and l > 0.0:
            rsi[i] = 0.0
        elif g == 0.0 and l == 0.0:
            rsi[i] = 50.0
        else:
            rs = g / l
            rsi[i] = 100.0 - (100.0 / (1.0 + rs))

    return pd.Series(rsi, index=series.index)

class LocalIndicatorService:
    """
    Computes technical analysis metrics locally in memory with strict point-in-time causality.
    Canonical Authoritative Indicator Module.
    """

    INDICATOR_COLUMNS = [
        "ema_20", "ema_50", "ema_100", "ema_200",
        "sma_20", "sma_50", "sma_200",
        "rsi_14", "macd", "macd_signal", "macd_hist",
        "bb_upper", "bb_middle", "bb_lower",
        "atr_14", "donchian_high_20", "donchian_low_20"
    ]

    @classmethod
    def calculate_indicators(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates RSI, MACD, EMAs, SMAs, Bollinger Bands, ATR, and 1-bar shifted Donchian Channels.
        Normalizes column names case-insensitively and initializes all indicator columns with NaN.
        """
        if df is None or df.empty:
            logger.warning("[Indicators] Empty input DataFrame provided.")
            return pd.DataFrame(columns=cls.INDICATOR_COLUMNS)

        df = df.copy()

        # Normalize column names to lowercase
        col_map = {c: str(c).strip().lower() for c in df.columns}
        df = df.rename(columns=col_map)

        # Initialize all indicator columns with NaN
        for col in cls.INDICATOR_COLUMNS:
            if col not in df.columns:
                df[col] = np.nan

        if "close" not in df.columns or len(df) < 2:
            logger.warning("[Indicators] Insufficient candles or missing close price.")
            return df

        close = pd.to_numeric(df["close"], errors="coerce").astype(float)

        # 1. Exponential Moving Averages
        if len(df) >= 20:
            df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        if len(df) >= 50:
            df["ema_50"] = close.ewm(span=50, adjust=False).mean()
        if len(df) >= 100:
            df["ema_100"] = close.ewm(span=100, adjust=False).mean()
        if len(df) >= 200:
            df["ema_200"] = close.ewm(span=200, adjust=False).mean()

        # 2. Simple Moving Averages
        if len(df) >= 20:
            df["sma_20"] = close.rolling(window=20).mean()
        if len(df) >= 50:
            df["sma_50"] = close.rolling(window=50).mean()
        if len(df) >= 200:
            df["sma_200"] = close.rolling(window=200).mean()

        # 3. Wilder's Relative Strength Index (RSI 14)
        if len(df) >= 14:
            df["rsi_14"] = compute_wilder_rsi(close, period=14)

        # 4. MACD (12, 26, 9)
        if len(df) >= 26:
            ema_12 = close.ewm(span=12, adjust=False).mean()
            ema_26 = close.ewm(span=26, adjust=False).mean()
            df["macd"] = ema_12 - ema_26
            df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
            df["macd_hist"] = df["macd"] - df["macd_signal"]

        # 5. Bollinger Bands (20, 2)
        if len(df) >= 20:
            sma_20 = df["sma_20"]
            std_20 = close.rolling(window=20).std()
            df["bb_upper"] = sma_20 + (std_20 * 2.0)
            df["bb_lower"] = sma_20 - (std_20 * 2.0)
            df["bb_middle"] = sma_20

        # 6. Average True Range (ATR 14)
        if "high" in df.columns and "low" in df.columns and len(df) >= 14:
            high = pd.to_numeric(df["high"], errors="coerce").astype(float)
            low = pd.to_numeric(df["low"], errors="coerce").astype(float)
            prev_close = close.shift(1)
            tr = pd.concat([
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs()
            ], axis=1).max(axis=1)
            df["atr_14"] = tr.rolling(window=14).mean()

        # 7. Donchian Channels (20) Shifted 1-bar for zero look-ahead point-in-time causality
        if "high" in df.columns and "low" in df.columns and len(df) >= 21:
            high = pd.to_numeric(df["high"], errors="coerce").astype(float)
            low = pd.to_numeric(df["low"], errors="coerce").astype(float)
            df["donchian_high_20"] = high.rolling(window=20).max().shift(1)
            df["donchian_low_20"] = low.rolling(window=20).min().shift(1)

        return df

    @classmethod
    def get_latest_metrics(cls, df: pd.DataFrame) -> dict:
        """
        Returns latest computed metric values as a dictionary.
        Returns None for any indicator that is unavailable or in warm-up/NaN state.
        """
        df_ind = cls.calculate_indicators(df)
        if df_ind is None or df_ind.empty:
            return {}
        latest = df_ind.iloc[-1]

        def get_clean_float(col_name: str) -> Optional[float]:
            if col_name in latest:
                val = latest.get(col_name)
                if val is not None and not pd.isna(val) and np.isfinite(float(val)):
                    return float(val)
            return None

        # Resolve close price key
        c_val = get_clean_float("close")

        res = {"close": c_val}
        for col in cls.INDICATOR_COLUMNS:
            res[col] = get_clean_float(col)

        return res
