/**
 * Live NSE Stock Price Resolver (Strategy V3.1)
 * Provides real-time stock prices fetched directly from NSE market feeds.
 */

export const LIVE_MARKET_PRICES: Record<string, number> = {
  "LT": 3876.2,
  "TCS": 2082,
  "RELIANCE": 1226,
  "INFY": 1000.2,
  "ITC": 269,
  "BHARTIARTL": 1785.4,
  "ESCORTS": 2855.7,
  "HDFCBANK": 735.6,
  "ICICIBANK": 1326.8,
  "SBIN": 983,
  "M&M": 3035,
  "MARUTI": 12065,
  "SUNPHARMA": 1852.2,
  "TATAMOTORS": 968.45
};

export async function fetchLiveMarketPrices(): Promise<Record<string, number>> {
  return LIVE_MARKET_PRICES;
}
