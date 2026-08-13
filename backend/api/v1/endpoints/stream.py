from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import datetime
from backend.core.container import container

router = APIRouter()

@router.get("/signals")
async def stream_signals(request: Request):
    """
    Vision 2.2: Turbo-Sync SSE Stream.
    Pushes real-time BOS/CHoCH and high-conviction opportunities.
    """
    async def event_generator():
        while True:
            try:
                # If client closes connection, stop sending
                if await request.is_disconnected():
                    break

                # 1. Fetch latest opportunities from repo
                opps = await container.ios_repo.get_active_opportunities(limit=3)

                if opps:
                    yield {
                        "event": "opportunity_update",
                        "id": str(datetime.datetime.utcnow().timestamp()),
                        "retry": 15000, # Retry every 15s if disconnected
                        "data": json.dumps([{
                            "symbol": o.symbol,
                            "type": o.type,
                            "conviction": o.conviction_score,
                            "thesis": o.ai_thesis,
                            "timestamp": o.timestamp.isoformat()
                        } for o in opps])
                    }

                # Wait before next check (Sub-second sync)
                await asyncio.sleep(5)
            except Exception as e:
                print(f"SSE Stream Error: {e}")
                await asyncio.sleep(5)

    return EventSourceResponse(event_generator())
