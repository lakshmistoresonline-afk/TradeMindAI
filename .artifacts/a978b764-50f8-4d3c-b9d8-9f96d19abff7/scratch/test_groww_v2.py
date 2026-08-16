import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        symbol = "RELIANCE"
        # Try Groww's internal chart API (often used in web frontend)
        # Structure: https://chart-service.groww.in/v1/charting/v1/chart/NSE/RELIANCE/1d?interval=1d&period=1m
        url = f"https://chart-service.groww.in/v1/charting/v1/chart/NSE/{symbol}/1d?interval=1d&period=1m"
        r = await client.get(url)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Sample: {r.text[:500]}")
        else:
            print(f"Body: {r.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test())
