"""
================================================================================
TradeMindAI: Data Import API Endpoint
================================================================================
POST /api/v1/data/import: Upload custom CSV/JSON tick/candle data directly into
local database tables without altering schema.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
import datetime
from backend.app.db.database import get_db
from backend.app.db.models import MarketData

router = APIRouter(prefix="/api/v1", tags=["Data Import"])

@router.post("/data/import")
async def import_custom_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Imports CSV or JSON tick/OHLCV data directly into local database tables.
    Expected columns: symbol, timestamp, open, high, low, close, volume.
    """
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV and JSON file uploads are supported.")

    content = await file.read()

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_json(io.BytesIO(content))

        # Standardize column names
        df.columns = [c.lower().strip() for c in df.columns]

        required_cols = {'symbol', 'timestamp', 'open', 'high', 'low', 'close'}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'volume' not in df.columns:
            df['volume'] = 0.0

        records_added = 0
        for _, row in df.iterrows():
            market_row = MarketData(
                symbol=str(row['symbol']).upper(),
                timestamp=row['timestamp'],
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            )
            db.merge(market_row) # Non-destructive upsert
            records_added += 1

        db.commit()

        return {
            "status": "SUCCESS",
            "filename": file.filename,
            "records_imported": records_added,
            "symbols_affected": list(df['symbol'].str.upper().unique())
        }

    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to parse and import data: {err}")
