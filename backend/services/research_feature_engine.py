import pandas as pd
import ta
from typing import Dict, Any

class ResearchFeatureEngine:
    """
    Phases 8-11: Research-Only Indicators and Challenger Model Features.
    ISOLATED from V2.2.
    """

    @staticmethod
    def calculate_research_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates additional indicators for research experiments.
        """
        if df.empty: return df

        # 1. Trend
        df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])

        # 2. Momentum
        df['RSI'] = ta.momentum.rsi(df['Close'])
        df['MFI'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])

        # 3. Volatility
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_Width'] = bb.bollinger_wband()

        # 4. Volume
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])

        return df

    @staticmethod
    def create_challenger_snapshot(symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Creates an indicator snapshot for a challenger model.
        """
        df_ind = ResearchFeatureEngine.calculate_research_indicators(df)
        last_row = df_ind.iloc[-1].to_dict()

        return {
            "symbol": symbol,
            "timestamp": df_ind.index[-1].isoformat(),
            "indicators": last_row
        }
