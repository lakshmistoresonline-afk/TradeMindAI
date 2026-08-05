from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.core.container import container

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def ai_chat(request: ChatRequest):
    response = await container.ai_provider.generate_analysis(request.message)
    return {"response": response}

@router.get("/consensus/{symbol}")
async def get_ai_consensus(symbol: str):
    stock = await container.repository.get_stock_by_symbol(symbol)
    if stock and stock.analysis:
        return {"consensus": stock.analysis.get("consensus"), "symbol": symbol}
    return {"consensus": "Data pending", "symbol": symbol}
