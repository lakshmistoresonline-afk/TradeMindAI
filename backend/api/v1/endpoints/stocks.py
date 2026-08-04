from fastapi import APIRouter, Depends
from backend.core.database import get_db
from google.cloud import firestore
import yfinance as yf

router = APIRouter()

@router.get("/market-stats")
async def get_market_stats():
    # Fetch real-time major indices
    indices = {
        "^NSEI": "NIFTY 50",
        "^NSEBANK": "BANK NIFTY",
        "^INDIAVIX": "India VIX"
    }
    stats = {}
    for symbol, name in indices.items():
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        stats[name] = {
            "value": round(info.last_price, 2),
            "change": round(((info.last_price - info.previous_close) / info.previous_close) * 100, 2)
        }
    return stats

@router.get("/")
async def get_stocks(db: firestore.Client = Depends(get_db)):
    stocks_ref = db.collection("stocks")
    docs = stocks_ref.stream()
    stocks = [doc.to_dict() for doc in docs]
    return stocks

@router.get("/{symbol}")
async def get_stock_detail(symbol: str, db: firestore.Client = Depends(get_db)):
    doc_ref = db.collection("stocks").document(symbol)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {"error": "Stock not found"}
