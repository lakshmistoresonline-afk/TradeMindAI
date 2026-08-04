from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
async def ai_chat(query: str):
    return {"response": f"AI response to: {query}"}

@router.get("/consensus/{symbol}")
async def get_ai_consensus(symbol: str):
    return {"consensus": "Buy", "symbol": symbol}
