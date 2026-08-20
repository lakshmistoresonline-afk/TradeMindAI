
import httpx
import asyncio
from datetime import datetime, timedelta

async def debug():
    base_url = "https://api.groww.in/v1"
    symbol = "NSE-GUJGASLTD"
    url = f"{base_url}/live/quote"
    params = {"symbol": symbol}

    async with httpx.AsyncClient() as client:
        print(f"Fetching {symbol} from {url}...")
        try:
            response = await client.get(url, params=params)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Data: {response.json()}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

asyncio.run(debug())
