import httpx
import asyncio
import json

async def check():
    base_url = "https://trademind-api-production.up.railway.app/api/v1"
    headers = {
        "Authorization": "Bearer internal_demo_token"
    }

    async with httpx.AsyncClient() as client:
        print(f"Checking {base_url}/stocks/ ...")
        try:
            r = await client.get(f"{base_url}/stocks/", headers=headers, timeout=10)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Count: {len(data)}")
                if data:
                    s = data[0]
                    print(f"Sample: {s.get('symbol')} | analysis: {bool(s.get('analysis'))} | consensus: {bool(s.get('structured_consensus'))}")
        except Exception as e:
            print(f"Error: {e}")

        print(f"\nChecking {base_url}/ios/signals/live ...")
        try:
            r = await client.get(f"{base_url}/ios/signals/live", headers=headers, timeout=10)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Count: {len(data)}")
                if data:
                    print(f"Sample: {data[0].get('symbol')} | {data[0].get('status')} | {data[0].get('timeframe')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
