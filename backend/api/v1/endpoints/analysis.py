from fastapi import APIRouter, BackgroundTasks
from backend.workers.tasks import analyze_nifty_50

router = APIRouter()

@router.post("/trigger")
async def trigger_full_analysis():
    # Trigger the Celery task
    task = analyze_nifty_50.delay()
    return {"message": "Batch analysis triggered", "task_id": task.id}

@router.get("/technical/{symbol}")
async def get_technical_analysis(symbol: str):
    return {"analysis": "technical", "symbol": symbol}

@router.get("/fundamental/{symbol}")
async def get_fundamental_analysis(symbol: str):
    return {"analysis": "fundamental", "symbol": symbol}
