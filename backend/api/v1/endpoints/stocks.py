from fastapi import APIRouter, Depends
from backend.core.database import get_db
from google.cloud import firestore

router = APIRouter()

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
