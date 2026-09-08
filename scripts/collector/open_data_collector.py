import httpx
import asyncio
import json
import time
from datetime import datetime
import os
from typing import List, Dict, Any

# --- CONFIGURATION ---
API_URL = "https://trademind-api-production.up.railway.app/api/v1/market-data/ingest"
COLLECTOR_KEY = "trademind-open-gateway-v1"
SCAN_INTERVAL = 60 # 1 minute
NIFTY_200_LIST = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "ITC", "LICI", "LT"]
INDEX_LIST = ["NIFTY", "BANKNIFTY"]

class OpenDataCollector:
    """
    TRADEMIND OPEN DATA COLLECTOR - Windows Gateway.
    Collects ₹0 cost market data from public sources and pushes to Railway API.
    Supports Equity and F&O.
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.cookies = None

    async def _init_nse_session(self):
        try:
            resp = await self.client.get("https://www.nseindia.com", headers=self.headers)
            self.cookies = resp.cookies
            print("[+] NSE Session Initialized.")
        except Exception as e:
            print(f"[!] NSE Session Error: {e}")

    async def fetch_equity_prices(self) -> List[Dict[str, Any]]:
        results = []
        if not self.cookies: await self._init_nse_session()

        for symbol in NIFTY_200_LIST:
            try:
                url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
                resp = await self.client.get(url, headers=self.headers, cookies=self.cookies)
                if resp.status_code == 200:
                    data = resp.json()
                    ltp = data.get("priceInfo", {}).get("lastPrice")
                    if ltp:
                        results.append({
                            "symbol": symbol,
                            "price": float(ltp),
                            "asset_class": "EQUITY",
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "NSE_PUBLIC"
                        })
                await asyncio.sleep(0.5)
            except: pass
        return results

    async def fetch_fno_prices(self) -> List[Dict[str, Any]]:
        results = []
        if not self.cookies: await self._init_nse_session()

        for symbol in INDEX_LIST:
            try:
                url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
                resp = await self.client.get(url, headers=self.headers, cookies=self.cookies)
                if resp.status_code == 200:
                    data = resp.json()
                    # Extract Spot
                    spot = data.get("records", {}).get("underlyingValue")
                    if spot:
                         results.append({
                             "symbol": symbol,
                             "price": float(spot),
                             "asset_class": "INDEX",
                             "timestamp": datetime.utcnow().isoformat(),
                             "source": "NSE_PUBLIC"
                         })

                    # Extract ATM Option Premium (Sample)
                    # Implementation for demonstration logic
                    filtered = data.get("filtered", {})
                    if filtered and filtered.get("data"):
                         atm_option = filtered["data"][0] # Just a sample
                         strike = atm_option.get("strikePrice")
                         ce_ltp = atm_option.get("CE", {}).get("lastPrice")
                         if ce_ltp:
                              results.append({
                                  "symbol": f"{symbol}{strike}CE",
                                  "price": float(ce_ltp),
                                  "asset_class": "OPTIONS",
                                  "underlying": symbol,
                                  "timestamp": datetime.utcnow().isoformat(),
                                  "source": "NSE_PUBLIC"
                              })
                await asyncio.sleep(1)
            except: pass
        return results

    async def push_to_backend(self, payload: List[Dict[str, Any]]):
        if not payload: return
        headers = {"X-Collector-Key": COLLECTOR_KEY, "Content-Type": "application/json"}
        try:
            await self.client.post(API_URL, json=payload, headers=headers)
            print(f"   [PUSH] Transmitted {len(payload)} items.")
        except Exception as e:
            print(f"[!] Push Failed: {e}")

    async def run(self):
        print("--- TRADEMIND OPEN DATA COLLECTOR STARTING ---")
        while True:
            try:
                e_prices = await self.fetch_equity_prices()
                f_prices = await self.fetch_fno_prices()
                await self.push_to_backend(e_prices + f_prices)
            except Exception as e:
                print(f"[!] Error: {e}")
            await asyncio.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    collector = OpenDataCollector()
    asyncio.run(collector.run())
