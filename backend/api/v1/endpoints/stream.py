import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from backend.core.container import container

router = APIRouter()

@router.get("/signals")
async def stream_signals(request: Request):
    """
    Server-Sent Events (SSE) for Real-Time Signal Updates.
    Vision 2.3: Durable connection with heartbeat.
    """
    async def event_generator():
        while True:
            # Check for disconnect
            if await request.is_disconnected():
                print("[Stream] Client disconnected.")
                break

            try:
                # 1. Fetch active opportunities/signals
                active = await container.ios_repo.get_active_opportunities(limit=10)

                # 2. Yield event
                if active:
                    yield {
                        "event": "opportunity_update",
                        "data": json.dumps([o.model_dump() if hasattr(o, 'model_dump') else o for o in active], default=str)
                    }

                # Heartbeat
                yield {
                    "event": "ping",
                    "data": "heartbeat"
                }

            except Exception as e:
                print(f"[Stream] Loop error: {e}")
                yield {
                    "event": "error",
                    "data": str(e)
                }

            # Throttled update rate (15s)
            await asyncio.sleep(15)

    return EventSourceResponse(event_generator())
