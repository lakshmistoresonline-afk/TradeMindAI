from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.core.container import container

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def ai_chat(request: ChatRequest):
    """
    Vision 2.2: Contextual AI Copilot.
    Injects current terminal intelligence (Regime, Flow, Opportunities)
    to provide grounded institutional responses.
    """
    from backend.core.container import container

    # 1. Fetch current context
    regime = await container.ios_repo.get_latest_regime()
    opps = await container.ios_repo.get_active_opportunities(limit=5)

    context_str = f"""
    CURRENT MARKET CONTEXT:
    - REGIME: {regime.regime if regime else 'NEUTRAL'}
    - RISK MODE: {regime.risk_mode if regime else 'NEUTRAL'}
    - VIX: {regime.volatility_index if regime else '15.0'}
    - TOP OPPORTUNITIES: {', '.join([o.symbol for o in opps]) if opps else 'Scanning...'}
    """

    # 2. Generate grounded response
    system_prompt = f"You are the TradeMind AI Institutional Assistant. {context_str}. Answer the user query based on this data."
    response = await container.ai_provider.generate_analysis(f"{system_prompt}\n\nUser Query: {request.message}")

    return {"response": response}

@router.get("/consensus/{symbol}")
async def get_ai_consensus(symbol: str):
    stock = await container.repository.get_stock_by_symbol(symbol)
    if stock and stock.analysis:
        return {"consensus": stock.analysis.get("consensus"), "symbol": symbol}
    return {"consensus": "Data pending", "symbol": symbol}
