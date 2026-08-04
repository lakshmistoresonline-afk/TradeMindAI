from fastapi import APIRouter

router = APIRouter()

@router.get("/technical/{symbol}")
async def get_technical_analysis(symbol: str):
    return {"analysis": "technical", "symbol": symbol}

@router.get("/fundamental/{symbol}")
async def get_fundamental_analysis(symbol: str):
    return {"analysis": "fundamental", "symbol": symbol}
