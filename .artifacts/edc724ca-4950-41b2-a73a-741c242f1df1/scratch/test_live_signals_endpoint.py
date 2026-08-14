import os
import sys
import asyncio
import json

# Add project root to path
sys.path.append("D:/TradeMindAI")

async def test():
    from backend.core.container import container
    from backend.domain.models.ios import LiveSignal

    print("Testing get_active_live_signals serialization...")
    try:
        signals = await container.ios_repo.get_active_live_signals()
        print(f"Successfully fetched {len(signals)} signals.")
        if signals:
            print("First signal sample:")
            print(signals[0].model_dump_json(indent=2))

            # Test JSON serialization which FastAPI does
            json_data = [s.model_dump() for s in signals]
            # Handle datetime serialization manually for printing
            def datetime_handler(x):
                if hasattr(x, "isoformat"):
                    return x.isoformat()
                raise TypeError("Unknown type")

            print("Serialization successful.")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
