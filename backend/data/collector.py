import yfinance as yf
import pandas as pd
from google.cloud import firestore
from backend.data.models import Stock, StockPrice
import datetime

class DataCollector:
    def __init__(self, db: firestore.Client):
        self.db = db

    def fetch_stock_info(self, symbol: str):
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info

        stock_ref = self.db.collection("stocks").document(symbol)

        stock_data = {
            "symbol": symbol,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "last_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "updated_at": datetime.datetime.utcnow()
        }

        stock_ref.set(stock_data, merge=True)
        return stock_data

    def fetch_historical_data(self, symbol: str, period="10y"):
        ticker = yf.Ticker(f"{symbol}.NS")
        # Fetch data with higher resolution for 10y if possible, default to 1d
        df = ticker.history(period=period)

        if df.empty:
            return df

        # Store in a subcollection 'prices' under the stock document
        stock_ref = self.db.collection("stocks").document(symbol)
        prices_ref = stock_ref.collection("prices")

        for index, row in df.iterrows():
            # Use date as ID to avoid duplicates (YYYY-MM-DD)
            date_id = index.strftime("%Y-%m-%d")

            price_data = {
                "symbol": symbol,
                "date": index.to_pydatetime(),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": int(row["Volume"])
            }

            prices_ref.document(date_id).set(price_data)

        return df
