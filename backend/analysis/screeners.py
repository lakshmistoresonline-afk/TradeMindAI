import pandas as pd

class Screeners:
    @staticmethod
    def rsi_oversold(df_dict: dict, threshold=30):
        results = []
        for symbol, df in df_dict.items():
            if df["RSI"].iloc[-1] < threshold:
                results.append(symbol)
        return results

    @staticmethod
    def golden_cross(df_dict: dict):
        results = []
        for symbol, df in df_dict.items():
            if df["EMA_50"].iloc[-1] > df["EMA_200"].iloc[-1] and \
               df["EMA_50"].iloc[-2] <= df["EMA_200"].iloc[-2]:
                results.append(symbol)
        return results

    @staticmethod
    def volume_spike(df_dict: dict, multiplier=2):
        results = []
        for symbol, df in df_dict.items():
            avg_vol = df["Volume"].iloc[-21:-1].mean()
            if df["Volume"].iloc[-1] > avg_vol * multiplier:
                results.append(symbol)
        return results
