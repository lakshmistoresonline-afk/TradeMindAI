import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        # Test historical candles (public endpoint often uses different structure)
        # We'll try the one from GrowwProvider
        symbol = "RELIANCE"
        url = f"https://api.groww.in/v1/stock/v1/chart/v1/candles/NSE/{symbol}?interval=1d&period=1m"
        r = await client.get(url)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Sample: {r.text[:500]}")
        else:
            print(f"Body: {r.text}")

if __name__ == "__main__":
    asyncio.run(test())
