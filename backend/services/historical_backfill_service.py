"""
================================================================================
TradeMindAI: 2015-to-Present Historical Price Backfill & Gap Updater Service
================================================================================
Expands database price coverage from 2015-01-01 to 2026-10-17 for Nifty 500 stocks
via authentic market-data source adapters (yfinance/NSE).
Synthetic sine-wave price generation is strictly forbidden.
================================================================================
"""

import os
import sys
import logging
import datetime
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import create_engine, text

from backend.core.postgres import SessionLocal, StockDB, PriceDB

logger = logging.getLogger(__name__)

class HistoricalBackfillService:
    """
    Ensures daily OHLCV price coverage from authentic market-data sources
    for all canonical Nifty 500 constituent equities.
    Synthetic price generation is strictly forbidden. Missing data remains missing.
    """

    START_DATE = datetime(2015, 1, 1)
    END_DATE = datetime(2026, 10, 17)

    @classmethod
    def fetch_authentic_source_bars(cls, symbol: str, start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
        """
        Attempts authentic market data fetch for symbol using yfinance/provider adapter.
        Fails closed with empty list if data is unavailable (no synthetic generation).
        """
        try:
            import yfinance as yf
            ticker_str = f"{symbol}.NS"
            df = yf.download(
                ticker_str,
                start=start_dt.strftime("%Y-%m-%d"),
                end=end_dt.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True
            )
            if df.empty:
                logger.warning(f"[Backfill] Authentic fetch returned no bars for {symbol}.")
                return []

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0].lower() for col in df.columns]
            else:
                df.columns = [col.lower() for col in df.columns]

            bars = []
            for idx_dt, row in df.iterrows():
                try:
                    c_open = float(row.get("open", 0))
                    c_high = float(row.get("high", 0))
                    c_low = float(row.get("low", 0))
                    c_close = float(row.get("close", 0))
                    c_vol = float(row.get("volume", 0))

                    if c_open > 0 and c_high > 0 and c_low > 0 and c_close > 0 and c_high >= c_low:
                        bars.append({
                            "symbol": symbol,
                            "date": idx_dt.to_pydatetime() if hasattr(idx_dt, "to_pydatetime") else idx_dt,
                            "open": c_open,
                            "high": c_high,
                            "low": c_low,
                            "close": c_close,
                            "volume": max(0.0, c_vol),
                            "source": "YFINANCE_AUTHENTIC"
                        })
                except Exception:
                    continue

            return bars
        except Exception as e:
            logger.warning(f"[Backfill] Source adapter fetch error for {symbol}: {e}")
            return []

    @classmethod
    def backfill_and_update_missing_dates(cls) -> Dict[str, Any]:
        logger.info(f"[*] Starting Authentic Historical Price Backfill Updater...")

        added_bars = 0
        stocks_processed = 0

        with SessionLocal() as session:
            stocks = session.query(StockDB).all()
            if not stocks:
                return {"status": "FAILED", "reason": "NO_STOCKS_FOUND"}

            expected_dates = pd.bdate_range(start=cls.START_DATE, end=cls.END_DATE)

            for stock in stocks:
                sym = stock.symbol
                existing = session.query(PriceDB.date).filter(PriceDB.symbol == sym).all()
                existing_dates = {pd.to_datetime(p[0]).normalize() for p in existing}

                missing_dates = [d for d in expected_dates if d.normalize() not in existing_dates]

                if not missing_dates:
                    stocks_processed += 1
                    continue

                # Fetch authentic market bars for gap period
                fetched_bars = cls.fetch_authentic_source_bars(sym, cls.START_DATE, cls.END_DATE)
                new_price_entries = []

                for bar_data in fetched_bars:
                    b_dt = pd.to_datetime(bar_data["date"]).normalize()
                    if b_dt in missing_dates:
                        new_price_entries.append(PriceDB(
                            symbol=sym,
                            date=bar_data["date"],
                            open=bar_data["open"],
                            high=bar_data["high"],
                            low=bar_data["low"],
                            close=bar_data["close"],
                            volume=bar_data["volume"],
                            source=bar_data["source"]
                        ))
                        added_bars += 1

                if new_price_entries:
                    session.bulk_save_objects(new_price_entries)
                    session.commit()

                stocks_processed += 1

        return {
            "status": "COMPLETED",
            "stocks_processed": stocks_processed,
            "added_bars": added_bars,
            "start_date": cls.START_DATE.strftime('%Y-%m-%d'),
            "end_date": cls.END_DATE.strftime('%Y-%m-%d')
        }
