import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple
import yfinance as yf
from sqlalchemy.orm import Session
from backend.app.db.models import MarketData
from backend.services.nifty200_universe_service import Nifty200UniverseService

class RealMarketDataIngestionService:
    @staticmethod
    def ingest_real_market_data(db: Session, period: str = "2y") -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Ingests real historical OHLCV data from yfinance for verified NIFTY constituents
        retrieved dynamically from the security master via Nifty200UniverseService.
        Fails closed if security master is unavailable or empty (NO hardcoded fallback).
        """
        success_count = 0
        failure_records = []

        # Fail closed: must obtain universe from security_master without fallback
        universe = Nifty200UniverseService.get_current_nifty200_universe(db)
        if not universe:
            raise RuntimeError("Authoritative security master returned empty universe. Ingestion aborted (fail-closed).")

        for item in universe:
            sym = item["symbol"]
            p_sym = item["provider_symbol"] # Must be explicitly mapped
            if not p_sym:
                failure_records.append({
                    "symbol": sym,
                    "provider_symbol": None,
                    "error_type": "MISSING_PROVIDER_SYMBOL",
                    "error_message": "Provider symbol explicitly required and missing",
                    "retry_count": 0,
                    "final_status": "SKIPPED"
                })
                continue

            try:
                df = yf.download(p_sym, period=period, interval="1d", progress=False)
                if df.empty or len(df) < 5:
                    failure_records.append({
                        "symbol": sym,
                        "provider_symbol": p_sym,
                        "error_type": "NO_DATA",
                        "error_message": "Empty DataFrame returned from yfinance",
                        "retry_count": 1,
                        "final_status": "NO_DATA"
                    })
                    continue

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]

                persisted_for_sym = 0
                for idx, row in df.iterrows():
                    open_p = float(row.get("Open", 0) or 0)
                    high_p = float(row.get("High", 0) or 0)
                    low_p = float(row.get("Low", 0) or 0)
                    close_p = float(row.get("Close", 0) or 0)
                    vol = float(row.get("Volume", 0) or 0)

                    # Validation
                    if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0 or vol < 0:
                        continue
                    if high_p < low_p or high_p < max(open_p, close_p) or low_p > min(open_p, close_p):
                        continue

                    ts = pd.to_datetime(idx).to_pydatetime()

                    existing = db.query(MarketData).filter(
                        MarketData.symbol == sym,
                        MarketData.timestamp == ts
                    ).first()

                    if existing:
                        existing.open = open_p
                        existing.high = high_p
                        existing.low = low_p
                        existing.close = close_p
                        existing.volume = vol
                    else:
                        m_row = MarketData(
                            symbol=sym,
                            timestamp=ts,
                            open=open_p,
                            high=high_p,
                            low=low_p,
                            close=close_p,
                            volume=vol
                        )
                        db.add(m_row)
                    persisted_for_sym += 1

                db.commit()
                success_count += 1
                print(f"[Ingestion] Success for {sym}: persisted {persisted_for_sym} rows.")

            except Exception as e:
                failure_records.append({
                    "symbol": sym,
                    "provider_symbol": p_sym,
                    "error_type": "PROVIDER_ERROR",
                    "error_message": str(e),
                    "retry_count": 1,
                    "final_status": "ERROR"
                })
                print(f"[Ingestion] Error for {sym}: {e}")

        return success_count, len(failure_records), failure_records
