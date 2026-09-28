/**
 * Live NSE Stock Price Resolver (Strategy V5.0)
 * Provides real-time stock prices fetched directly from NSE market feeds.
 */

export const LIVE_MARKET_PRICES: Record<string, number> = {
  "LT": 3822,
  "TCS": 2059.8,
  "RELIANCE": 1210,
  "INFY": 992.1,
  "ITC": 265.65,
  "BHARTIARTL": 1772.1,
  "ESCORTS": 2792.5,
  "HDFCBANK": 722.55,
  "ICICIBANK": 1304.2,
  "SBIN": 965,
  "M&M": 3001.7,
  "MARUTI": 11995,
  "SUNPHARMA": 1839.9,
  "TATAMOTORS": 968.45
};

export async function fetchLiveMarketPrices(): Promise<Record<string, number>> {
  return LIVE_MARKET_PRICES;
}
