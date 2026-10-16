"""
================================================================================
TradeMindAI: SMC & ICT Pattern Detection (v2.0-SMC)
================================================================================
Implements causal Structure-Aware Order Block and Fair Value Gap (FVG) detection
according to the canonical SMC v2.0 strategy specification.
Enforces strict input validation and precise confirmation timestamp contracts
(FVG confirmed upon candle 3 completion; Order Block confirmed upon displacement candle completion).
"""

from typing import Any, List, Dict
import pandas as pd
import numpy as np

class SMCAnalysis:
    @staticmethod
    def _validate_input_df(df: Any) -> pd.DataFrame:
        """
        Validates input DataFrame for SMC detection.
        Rejects non-DataFrame inputs, missing OHLC columns, non-finite values,
        invalid OHLC geometry, duplicate columns (case-insensitive normalized),
        and unordered/duplicate timestamps.
        """
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Input DataFrame is empty, None, or not a pandas DataFrame.")

        df_norm = df.copy()
        cols = [str(c).strip().capitalize() for c in df_norm.columns]
        if len(cols) != len(set(cols)):
            raise ValueError(f"Duplicate columns detected after normalization: {list(df.columns)}")
        df_norm.columns = cols

        required = ["Open", "High", "Low", "Close"]
        for col in required:
            if col not in df_norm.columns:
                raise ValueError(f"Missing required column for SMC detection: {col}. Available: {list(df_norm.columns)}")

        # Check DatetimeIndex
        if not isinstance(df_norm.index, pd.DatetimeIndex):
            try:
                df_norm.index = pd.to_datetime(df_norm.index)
            except Exception as e:
                raise ValueError(f"DataFrame index cannot be parsed as DatetimeIndex: {e}") from e

        if not df_norm.index.is_monotonic_increasing:
            raise ValueError("DataFrame index timestamps are not monotonically increasing.")

        if df_norm.index.duplicated().any():
            raise ValueError("Duplicate timestamps detected in DataFrame index.")

        # Check finite numeric values
        for col in ["Open", "High", "Low", "Close"]:
            s = pd.to_numeric(df_norm[col], errors='coerce')
            if s.isna().any() or not np.isfinite(s).all():
                raise ValueError(f"Column {col} contains non-finite or non-numeric values.")
            df_norm[col] = s

        # Check OHLC geometry
        if ((df_norm["Low"] > df_norm["Open"]) | (df_norm["Low"] > df_norm["Close"]) |
            (df_norm["High"] < df_norm["Open"]) | (df_norm["High"] < df_norm["Close"]) |
            (df_norm["High"] < df_norm["Low"])).any():
            raise ValueError("Invalid OHLC geometry detected in input data for SMC detection.")

        return df_norm

    @staticmethod
    def detect_order_blocks(df: Any) -> List[Dict[str, Any]]:
        """
        SMC v2.0: Structure-Aware Order Block Detection (Canonical Specification).
        Bullish OB: Last down candle (index i-1) before displacement up where Close[i] > High[i-1] * 1.01.
        Bearish OB: Last up candle (index i-1) before displacement down where Close[i] < Low[i-1] * 0.99.
        Confirmed at index i (displacement candle completion).
        """
        df_valid = SMCAnalysis._validate_input_df(df)
        if len(df_valid) < 2:
            return []

        order_blocks = []
        for i in range(1, len(df_valid)):
            # Bullish OB (Last down candle before a displacement up)
            if df_valid["Close"].iloc[i] > df_valid["High"].iloc[i-1] * 1.01:
                if df_valid["Close"].iloc[i-1] < df_valid["Open"].iloc[i-1]:
                    order_blocks.append({
                        "type": "bullish",
                        "price": float(df_valid["Low"].iloc[i-1]),
                        "strength": "HIGH",
                        "zone_index": int(i-1),
                        "confirmation_index": int(i),
                        "confirmation_timestamp": df_valid.index[i]
                    })

            # Bearish OB (Last up candle before a displacement down)
            elif df_valid["Close"].iloc[i] < df_valid["Low"].iloc[i-1] * 0.99:
                if df_valid["Close"].iloc[i-1] > df_valid["Open"].iloc[i-1]:
                    order_blocks.append({
                        "type": "bearish",
                        "price": float(df_valid["High"].iloc[i-1]),
                        "strength": "HIGH",
                        "zone_index": int(i-1),
                        "confirmation_index": int(i),
                        "confirmation_timestamp": df_valid.index[i]
                    })

        return order_blocks

    @staticmethod
    def detect_structure_change(df: Any):
        events = SMCAnalysis.detect_structure_change_multi(df)
        if events:
            return events[-1]
        return {"type": "NONE", "level": 0.0}

    @staticmethod
    def detect_structure_change_multi(df: Any) -> list:
        df_valid = SMCAnalysis._validate_input_df(df)
        if len(df_valid) < 20:
            return []

        events = []
        for i in range(20, len(df_valid)):
            window = df_valid.iloc[i-20:i]
            high = window["High"].max()
            low = window["Low"].min()
            current = df_valid.iloc[i]

            if current["Close"] > high:
                events.append({
                    "type": "BOS",
                    "bias": "BULLISH",
                    "level": float(high),
                    "date": current.name,
                    "price": float(current["Close"])
                })
            elif current["Close"] < low:
                events.append({
                    "type": "BOS",
                    "bias": "BEARISH",
                    "level": float(low),
                    "date": current.name,
                    "price": float(current["Close"])
                })

        filtered = []
        if events:
            filtered.append(events[0])
            for e in events[1:]:
                if (e['date'] - filtered[-1]['date']).days > 5:
                    filtered.append(e)
        return filtered

    @staticmethod
    def detect_fvg(df: Any) -> List[Dict[str, Any]]:
        """
        SMC v2.0: Fair Value Gap Detection with strict 3-candle confirmation contract.
        Pattern is formed around candle 2 (index i), and confirmed upon completion of candle 3 (index i+1).
        """
        df_valid = SMCAnalysis._validate_input_df(df)
        if len(df_valid) < 3:
            return []

        fvgs = []
        for i in range(1, len(df_valid) - 1):
            # Bullish FVG: Low of candle 3 (i+1) > High of candle 1 (i-1)
            if df_valid["Low"].iloc[i+1] > df_valid["High"].iloc[i-1]:
                fvgs.append({
                    "type": "bullish",
                    "top": float(df_valid["Low"].iloc[i+1]),
                    "bottom": float(df_valid["High"].iloc[i-1]),
                    "pattern_index": int(i),
                    "confirmation_index": int(i+1),
                    "confirmation_timestamp": df_valid.index[i+1]
                })
            # Bearish FVG: High of candle 3 (i+1) < Low of candle 1 (i-1)
            elif df_valid["High"].iloc[i+1] < df_valid["Low"].iloc[i-1]:
                fvgs.append({
                    "type": "bearish",
                    "top": float(df_valid["Low"].iloc[i-1]),
                    "bottom": float(df_valid["High"].iloc[i+1]),
                    "pattern_index": int(i),
                    "confirmation_index": int(i+1),
                    "confirmation_timestamp": df_valid.index[i+1]
                })

        return fvgs
