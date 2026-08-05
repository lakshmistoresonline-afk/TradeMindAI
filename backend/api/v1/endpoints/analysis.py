from fastapi import APIRouter, BackgroundTasks, Depends
from backend.workers.tasks import analyze_nifty_50, run_adhoc_backtest
from backend.core.database import get_db
from google.cloud import firestore

router = APIRouter()

@router.post("/trigger")
async def trigger_full_analysis(period: str = "10y"):
    # Trigger the Celery task with 10y period
    task = analyze_nifty_50.delay(period=period)
    return {"message": f"Batch analysis triggered for {period}", "task_id": task.id}

@router.post("/backtest/{symbol}")
async def trigger_backtest(symbol: str):
    task = run_adhoc_backtest.delay(symbol)
    return {"message": "Backtest triggered", "task_id": task.id}

@router.get("/backtest/{symbol}")
async def get_backtest_results(symbol: str, db: firestore.Client = Depends(get_db)):
    doc = db.collection("backtests").document(symbol).get()
    if doc.exists:
        return doc.to_dict()
    return {"error": "No backtest report found"}

@router.get("/backtest/{symbol}/signals")
async def get_backtest_signals(symbol: str, db: firestore.Client = Depends(get_db)):
    signals_ref = db.collection("backtests").document(symbol).collection("signals")
    docs = signals_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(100).stream()
    signals = [doc.to_dict() for doc in docs]
    return signals

@router.get("/technical/{symbol}")
async def get_technical_analysis(symbol: str):
    return {"analysis": "technical", "symbol": symbol}

@router.get("/fundamental/{symbol}")
async def get_fundamental_analysis(symbol: str):
    return {"analysis": "fundamental", "symbol": symbol}
