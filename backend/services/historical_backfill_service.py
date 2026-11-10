"""
================================================================================
TradeMindAI: 2015-to-Present Historical Price Backfill & Gap Updater Service (v3.0)
================================================================================
Expands database price coverage from 2015-01-01 through dynamic completed market as-of date
for canonical Nifty 500 stocks via authentic market-data source adapters (yfinance/NSE).
Enforces auto_adjust=True price policy across ingestion, indicators, and signals.
Rejects non-finite values (NaN/Inf), negative volume, non-positive prices, and geometry violations.
Synthetic price generation is strictly forbidden.
================================================================================
"""

import os
import sys
import logging
import pytz
import numpy as np
import pandas as pd
import datetime
from datetime import datetime, time as dtime, timezone
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy import create_engine, text

from backend.core.postgres import SessionLocal, StockDB, PriceDB

logger = logging.getLogger(__name__)

KOLKATA_TZ = pytz.timezone("Asia/Kolkata")
AUTO_ADJUST_POLICY = True  # Corporate-action adjusted price basis policy across ingestion, indicators, and backtesting

class HistoricalBackfillService:
    """
    Ensures daily OHLCV price coverage from authentic market-data sources
    for all canonical Nifty 500 constituent equities.
    Synthetic price generation is strictly forbidden. Missing data remains missing.
    """

    START_DATE = datetime(2015, 1, 1)

    @classmethod
    def get_as_of_end_date(cls, ref_dt: Optional[datetime] = None) -> datetime:
        """
        Calculates the last completed market trading day in Asia/Kolkata timezone.
        Never treats an incomplete current trading session as a completed daily bar.
        """
        now_kol = ref_dt if ref_dt is not None else datetime.now(KOLKATA_TZ)
        today_date = now_kol.date()

        # If today is a weekday and time is before 15:30 IST (market close), completed day is yesterday
        if now_kol.weekday() < 5 and now_kol.time() < dtime(15, 30):
            completed_date = today_date - timedelta(days=1)
        else:
            completed_date = today_date

        # Roll backward if completed_date falls on a weekend
        while completed_date.weekday() >= 5:
            completed_date -= timedelta(days=1)

        return datetime(completed_date.year, completed_date.month, completed_date.day)

    @classmethod
    def validate_historical_bar(cls, symbol: str, date_obj: datetime, row: pd.Series, as_of_end_dt: datetime) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates individual daily OHLCV bar.
        Returns (is_valid, bar_dict, rejection_reason).
        """
        # Filter current incomplete candle if date_obj is after as_of_end_dt
        bar_date = date_obj.date() if isinstance(date_obj, (datetime, pd.Timestamp)) else date_obj
        if bar_date > as_of_end_dt.date():
            return False, None, f"INCOMPLETE_SESSION: Candle date {bar_date} is after completed as-of date {as_of_end_dt.date()}"

        try:
            c_open = float(row.get("open", row.get("Open", 0)))
            c_high = float(row.get("high", row.get("High", 0)))
            c_low = float(row.get("low", row.get("Low", 0)))
            c_close = float(row.get("close", row.get("Close", 0)))
            c_vol = float(row.get("volume", row.get("Volume", 0)))
        except (ValueError, TypeError):
            return False, None, "TYPE_CONVERSION_FAILURE: Non-numeric price/volume string"

        # Check finite numbers (NaN / Infinity)
        if not all(np.isfinite([c_open, c_high, c_low, c_close, c_vol])):
            return False, None, "NON_FINITE_VALUE: Contains NaN or Infinity"

        # Positive prices check
        if c_open <= 0 or c_high <= 0 or c_low <= 0 or c_close <= 0:
            return False, None, f"NON_POSITIVE_PRICE: Open={c_open}, High={c_high}, Low={c_low}, Close={c_close}"

        # Non-negative volume check (reject negative volume, do not silently convert)
        if c_vol < 0:
            return False, None, f"NEGATIVE_VOLUME: Volume={c_vol}"

        # Geometry checks
        if c_high < c_low or c_high < c_open or c_high < c_close or c_low > c_open or c_low > c_close:
            return False, None, f"GEOMETRY_VIOLATION: Open={c_open}, High={c_high}, Low={c_low}, Close={c_close}"

        valid_bar = {
            "symbol": symbol,
            "date": datetime(bar_date.year, bar_date.month, bar_date.day),
            "open": c_open,
            "high": c_high,
            "low": c_low,
            "close": c_close,
            "volume": c_vol,
            "source": "YFINANCE_AUTHENTIC",
            "auto_adjusted": AUTO_ADJUST_POLICY
        }
        return True, valid_bar, None

    @classmethod
    def fetch_authentic_source_bars(cls, symbol: str, start_dt: datetime, end_dt: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Attempts authentic market data fetch for symbol using yfinance/provider adapter.
        Fails closed with empty list if data is unavailable (no synthetic generation).
        """
        bars, _ = cls.fetch_authentic_source_bars_with_audit(symbol, start_dt, end_dt)
        return bars

    @classmethod
    def fetch_authentic_source_bars_with_audit(cls, symbol: str, start_dt: datetime, end_dt: Optional[datetime] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Fetches and validates authentic market bars for symbol.
        Returns (valid_bars, rejected_records).
        """
        as_of_end = end_dt or cls.get_as_of_end_date()
        valid_bars = []
        rejected_records = []

        try:
            import yfinance as yf
            ticker_str = f"{symbol}.NS"
            df = yf.download(
                ticker_str,
                start=start_dt.strftime("%Y-%m-%d"),
                end=(as_of_end + timedelta(days=1)).strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=AUTO_ADJUST_POLICY
            )
            if df.empty:
                logger.warning(f"[Backfill] Authentic fetch returned no bars for {symbol}.")
                return [], []

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0].lower() for col in df.columns]
            else:
                df.columns = [col.lower() for col in df.columns]

            for idx_dt, row in df.iterrows():
                dt_pydatetime = idx_dt.to_pydatetime() if hasattr(idx_dt, "to_pydatetime") else idx_dt
                is_valid, bar_dict, rej_reason = cls.validate_historical_bar(symbol, dt_pydatetime, row, as_of_end)

                if is_valid and bar_dict:
                    valid_bars.append(bar_dict)
                else:
                    rejected_records.append({
                        "symbol": symbol,
                        "date": str(dt_pydatetime),
                        "reason": rej_reason
                    })

            return valid_bars, rejected_records
        except Exception as e:
            logger.warning(f"[Backfill] Source adapter fetch error for {symbol}: {e}")
            return [], []

    @classmethod
    def backfill_and_update_missing_dates(cls, as_of_end_dt: Optional[datetime] = None) -> Dict[str, Any]:
        end_dt = as_of_end_dt or cls.get_as_of_end_date()
        logger.info(f"[*] Starting Authentic Historical Price Backfill Updater (Start: {cls.START_DATE.strftime('%Y-%m-%d')}, End: {end_dt.strftime('%Y-%m-%d')})...")

        added_bars = 0
        stocks_processed = 0
        total_rejected = 0

        with SessionLocal() as session:
            stocks = session.query(StockDB).all()
            if not stocks:
                return {"status": "FAILED", "reason": "NO_STOCKS_FOUND"}

            expected_dates = pd.bdate_range(start=cls.START_DATE, end=end_dt)

            for stock in stocks:
                sym = stock.symbol
                existing = session.query(PriceDB.date).filter(PriceDB.symbol == sym).all()
                existing_dates = {pd.to_datetime(p[0]).normalize() for p in existing}

                missing_dates = [d for d in expected_dates if d.normalize() not in existing_dates]

                if not missing_dates:
                    stocks_processed += 1
                    continue

                # Fetch authentic market bars for gap period
                fetched_bars, rejected = cls.fetch_authentic_source_bars_with_audit(sym, cls.START_DATE, end_dt)
                total_rejected += len(rejected)
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
            "total_rejected_bars": total_rejected,
            "start_date": cls.START_DATE.strftime('%Y-%m-%d'),
            "end_date": end_dt.strftime('%Y-%m-%d'),
            "auto_adjust_policy": AUTO_ADJUST_POLICY
        }
