"""
================================================================================
TradeMindAI: Local Indicator Service (v2.8-HARDENED-PERIOD-POLICY)
================================================================================
Computes technical analysis metrics locally across historical price candles:
RSI (14 Wilder Exponential Smoothing), MACD (12, 26, 9), EMA (20, 50, 200),
Bollinger Bands (20, 2), ATR (14), and Shifted Donchian Channels (20).
================================================================================
"""

import logging
import numpy as np
import pandas as pd

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
    """

    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates RSI, MACD, EMAs, Bollinger Bands, ATR, and 1-bar shifted Donchian Channels.
        """
        if df.empty or len(df) < 14:
            logger.warning("[Indicators] Insufficient candles for indicator calculation.")
            return df

        df = df.copy()
        close = df["close"]

        # 1. Exponential Moving Averages (EMA 20, 50, 200)
        df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        df["ema_50"] = close.ewm(span=50, adjust=False).mean()
        if len(df) >= 200:
            df["ema_200"] = close.ewm(span=200, adjust=False).mean()
        else:
            df["ema_200"] = np.nan

        # 2. Wilder's Relative Strength Index (RSI 14)
        df["rsi_14"] = compute_wilder_rsi(close, period=14)

        # 3. MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # 4. Bollinger Bands (20, 2) and SMA 20
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df["bb_upper"] = sma_20 + (std_20 * 2.0)
        df["bb_lower"] = sma_20 - (std_20 * 2.0)
        df["bb_middle"] = sma_20
        df["sma_20"] = sma_20

        # 5. Average True Range (ATR 14)
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            prev_close = close.shift(1)
            tr = pd.concat([
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs()
            ], axis=1).max(axis=1)
            df["atr_14"] = tr.rolling(window=14).mean()
        else:
            df["atr_14"] = np.nan

        # 6. Donchian Channels (20) Shifted 1-bar for zero look-ahead point-in-time causality
        if "high" in df.columns and "low" in df.columns and len(df) >= 21:
            df["donchian_high_20"] = df["high"].rolling(window=20).max().shift(1)
            df["donchian_low_20"] = df["low"].rolling(window=20).min().shift(1)
        else:
            df["donchian_high_20"] = np.nan
            df["donchian_low_20"] = np.nan

        return df

    @staticmethod
    def get_latest_metrics(df: pd.DataFrame) -> dict:
        """
        Returns latest computed metric values as a dictionary.
        Returns None for any indicator that is unavailable or in warm-up/NaN state.
        """
        df_ind = LocalIndicatorService.calculate_indicators(df)
        if df_ind.empty:
            return {}
        latest = df_ind.iloc[-1]
        return {
            "close": float(latest["close"]) if "close" in latest and not pd.isna(latest.get("close")) else None,
            "rsi_14": float(latest["rsi_14"]) if not pd.isna(latest.get("rsi_14")) else None,
            "ema_20": float(latest["ema_20"]) if not pd.isna(latest.get("ema_20")) else None,
            "ema_50": float(latest["ema_50"]) if not pd.isna(latest.get("ema_50")) else None,
            "ema_200": float(latest["ema_200"]) if not pd.isna(latest.get("ema_200")) else None,
            "macd": float(latest["macd"]) if not pd.isna(latest.get("macd")) else None,
            "macd_hist": float(latest["macd_hist"]) if not pd.isna(latest.get("macd_hist")) else None,
            "bb_upper": float(latest["bb_upper"]) if not pd.isna(latest.get("bb_upper")) else None,
            "bb_lower": float(latest["bb_lower"]) if not pd.isna(latest.get("bb_lower")) else None,
            "sma_20": float(latest["sma_20"]) if not pd.isna(latest.get("sma_20")) else None,
            "atr_14": float(latest["atr_14"]) if not pd.isna(latest.get("atr_14")) else None,
            "donchian_high_20": float(latest["donchian_high_20"]) if not pd.isna(latest.get("donchian_high_20")) else None,
            "donchian_low_20": float(latest["donchian_low_20"]) if not pd.isna(latest.get("donchian_low_20")) else None,
        }
