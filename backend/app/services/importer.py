"""
================================================================================
TradeMindAI: Non-Destructive Local CSV Importer Service
================================================================================
Reads custom OHLCV CSV/JSON data into local database tables with non-destructive
composite key deduplication to preserve existing database records.
"""

import io
import logging
import pandas as pd
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.db.models import MarketData

logger = logging.getLogger(__name__)

class LocalCSVImporterService:
    """
    Non-destructive importer for custom OHLCV tick and candle files.
    """

    @staticmethod
    def import_file(file_content: bytes, filename: str, db: Session) -> Dict[str, Any]:
        """
        Parses CSV or JSON content and imports into `app_market_data` table without schema mutation.
        """
        if not filename.endswith(('.csv', '.json')):
            raise ValueError("Only CSV and JSON files are supported.")

        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_json(io.BytesIO(file_content))

        # Standardize column headers
        df.columns = [c.lower().strip() for c in df.columns]

        required_cols = {'symbol', 'timestamp', 'open', 'high', 'low', 'close'}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required CSV columns: {missing}")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'volume' not in df.columns:
            df['volume'] = 0.0

        records_imported = 0
        records_skipped = 0

        for _, row in df.iterrows():
            sym = str(row['symbol']).strip().upper()
            ts = row['timestamp'].to_pydatetime() if hasattr(row['timestamp'], 'to_pydatetime') else row['timestamp']

            # Non-destructive check for existing composite key
            existing = db.query(MarketData).filter(
                MarketData.symbol == sym,
                MarketData.timestamp == ts
            ).first()

            if existing:
                records_skipped += 1
                continue

            market_row = MarketData(
                symbol=sym,
                timestamp=ts,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            )
            db.add(market_row)
            records_imported += 1

        db.commit()
        logger.info(f"[CSV Importer] Imported {records_imported} rows, skipped {records_skipped} duplicates.")

        # Refresh SignalCache for affected symbols
        try:
            from backend.app.services.market_data_service import LocalMarketDataService
            from backend.app.services.signal_engine import SignalEngine
            from backend.app.db.models import SignalCache, NewsArticle

            for sym in df['symbol'].str.upper().unique():
                df_sym = LocalMarketDataService.get_historical_data(sym, limit=180)
                if not df_sym.empty:
                    news = db.query(NewsArticle).filter(NewsArticle.symbol.ilike(sym)).first()
                    news_text = news.content if news else ""
                    res = SignalEngine.generate_signal(df_sym, news_text)
                    m = res.get("metrics", {})

                    cache_entry = db.query(SignalCache).filter(SignalCache.symbol == sym).first()
                    if not cache_entry:
                        cache_entry = SignalCache(symbol=sym, signal_type=res["signal_type"], confidence=res["confidence"])
                        db.add(cache_entry)

                    cache_entry.signal_type = res["signal_type"]
                    cache_entry.confidence = res["confidence"]
                    cache_entry.rsi_14 = m.get("rsi_14", 50.0)
                    cache_entry.macd_val = m.get("macd", 0.0)
                    cache_entry.macd_signal = m.get("macd_signal", 0.0)
                    cache_entry.ema_20 = m.get("ema_20", 0.0)
                    cache_entry.ema_50 = m.get("ema_50", 0.0)
            db.commit()
        except Exception as cache_err:
            logger.warning(f"[CSV Importer] SignalCache refresh notice: {cache_err}")

        return {
            "status": "SUCCESS",
            "filename": filename,
            "records_imported": records_imported,
            "records_skipped": records_skipped,
            "symbols": list(df['symbol'].str.upper().unique())
        }
