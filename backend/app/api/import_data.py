"""
================================================================================
TradeMindAI: Data Import API Endpoint
================================================================================
POST /api/v1/data/import: Upload custom CSV/JSON tick/candle data directly into
local database tables with strict administrative checks, size limits, and validation.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
import datetime
import math
from backend.app.db.database import get_db
from backend.app.db.models import MarketData
from backend.core.auth import get_current_admin

router = APIRouter(prefix="/api/v1", tags=["Data Import"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_ROWS = 50000

@router.post("/data/import")
async def import_custom_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Imports CSV or JSON tick/OHLCV data directly into database tables with validation.
    Expected columns: symbol, timestamp, open, high, low, close, volume.
    Protected by administrative access.
    """
    if not file.filename or not file.filename.lower().endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV and JSON file uploads are supported.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File size exceeds the 10MB upload limit.")

    try:
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_json(io.BytesIO(content))

        if len(df) > MAX_ROWS:
            raise HTTPException(status_code=413, detail=f"Row count exceeds maximum limit of {MAX_ROWS} rows.")

        # Standardize column names
        df.columns = [c.lower().strip() for c in df.columns]

        required_cols = {'symbol', 'timestamp', 'open', 'high', 'low', 'close'}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise HTTPException(status_code=422, detail=f"Missing required columns: {list(missing)}")

        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        if df['timestamp'].isnull().any():
            raise HTTPException(status_code=422, detail="Invalid timestamp format detected in upload.")

        if 'volume' not in df.columns:
            df['volume'] = 0.0

        records_added = 0
        symbols_affected = set()

        with db.begin(): # Bounded transaction with automatic rollback on exception
            for _, row in df.iterrows():
                sym = str(row['symbol']).upper().strip()
                if not sym or len(sym) > 20:
                    raise HTTPException(status_code=422, detail=f"Invalid symbol: {sym}")

                try:
                    o = float(row['open'])
                    h = float(row['high'])
                    l = float(row['low'])
                    c = float(row['close'])
                    v = float(row['volume'])
                except (ValueError, TypeError):
                    raise HTTPException(status_code=422, detail="Non-numeric value encountered in price or volume columns.")

                if not (math.isfinite(o) and math.isfinite(h) and math.isfinite(l) and math.isfinite(c) and math.isfinite(v)):
                    raise HTTPException(status_code=422, detail="Non-finite numeric value encountered.")

                # OHLC consistency validation
                if h < l or h < o or h < c or l > o or l > c or o <= 0 or h <= 0 or l <= 0 or c <= 0:
                    raise HTTPException(status_code=422, detail=f"Invalid OHLC candle relationship for symbol {sym}.")

                market_row = MarketData(
                    symbol=sym,
                    timestamp=row['timestamp'],
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    volume=v
                )
                db.merge(market_row)
                records_added += 1
                symbols_affected.add(sym)

        return {
            "status": "SUCCESS",
            "filename": file.filename,
            "records_imported": records_added,
            "symbols_affected": list(symbols_affected)
        }

    except HTTPException as he:
        raise he
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the data import.")
