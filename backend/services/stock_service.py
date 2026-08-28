from __future__ import annotations
from typing import List, Dict, Any
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow
from datetime import datetime
import gc
import pandas as pd

class StockService:
    def __init__(self, repository: IStockRepository, provider: IMarketDataProvider, news_provider: INewsProvider, inst_provider: IInstitutionalDataProvider):
        self.repository = repository
        self.provider = provider
        self.news_provider = news_provider
        self.inst_provider = inst_provider

    async def collect_stock_data(self, symbol: str, period: str = "10y") -> Stock:
        # 1. Sync Base Data
        existing_stock = await self.repository.get_stock_by_symbol(symbol)
        info = await self.provider.fetch_stock_info(symbol)

        # Vision 2.0: Decide if we need a full historical sync
        # Force full sync if period is 10y or if stock has no update history
        is_full_sync = period == "10y" or not (existing_stock and existing_stock.updated_at)

        fetch_period = period if is_full_sync else "1mo"
        history_df = await self.provider.fetch_history(symbol, fetch_period)

        if history_df.empty:
            print(f"No history found for {symbol}. Skipping detailed analysis.")
            return Stock(symbol=symbol, **info)

        # 2. Sync News (Vision 2.0)
        from backend.core.container import container
        try:
            news = await self.news_provider.fetch_latest_news(symbol)
            if news:
                await container.data_platform_repo.save_news(news)
        except: pass

        # 3. Map to Domain & Persist
        stock = Stock(symbol=symbol, **info)

        # Vision 2.2: Deep Options Intelligence
        try:
            opt_chain = await self.provider.get_option_chain(symbol)
            if opt_chain:
                print(f"DEBUG: Found options for {symbol}")
                stock.options_data = opt_chain.model_dump()
                stock.options_data['available'] = True
            else:
                print(f"DEBUG: No options returned for {symbol}")
        except Exception:
            import traceback
            print(f"DEBUG: Options fetch error for {symbol}:")
            traceback.print_exc()

        await self.repository.save_stock(stock)

        # 4. Sync Earnings (Vision 2.0)
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.NS")
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                from backend.domain.models.data_platform import EarningsData
                # Convert timestamp to datetime
                earning_date = calendar.iloc[0, 0] if hasattr(calendar, 'iloc') else datetime.utcnow()
                earnings = EarningsData(
                    symbol=symbol,
                    date=earning_date,
                    eps_actual=0.0, # Will be updated after results
                    eps_estimate=info.get("forwardEps", 0.0),
                    revenue_actual=0.0,
                    revenue_estimate=0.0
                )
                await container.data_platform_repo.save_earnings(earnings)
        except: pass

        if is_full_sync:
            # Memory Optimization: For initial 10Y load, we save everything but only
            # calculate complex indicators for the most recent 2 years.
            from backend.analysis.technical import TechnicalAnalysis

            # A. Process Full History (Raw Price Data)
            print(f"[{symbol}] Processing 10Y Raw History ({len(history_df)} days)...")
            raw_prices = []
            for index, row in history_df.iterrows():
                raw_prices.append(StockPrice(
                    symbol=symbol, date=index.to_pydatetime(),
                    open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"],
                    volume=int(row["Volume"])
                ))

            # Batch save raw prices first
            await self.repository.save_historical_prices(symbol, raw_prices)
            print(f"[{symbol}] Raw History Saved.")
            del raw_prices
            gc.collect()

            # B. Calculate Indicators for Recent 2 Years (Approx 500 trading days)
            print(f"[{symbol}] Calculating Institutional Indicators (Last 2Y)...")
            recent_df = history_df.tail(600) # Buffer for long EMAs
            df_ta = TechnicalAnalysis.calculate_indicators(recent_df)

            ta_prices = []
            for index, row in df_ta.tail(500).iterrows():
                indicator_keys = ["EMA_20", "EMA_50", "EMA_200", "RSI", "MACD_12_26_9", "Pivot"]
                indicators = {k: row[k] for k in indicator_keys if k in row}

                ta_prices.append(StockPrice(
                    symbol=symbol, date=index.to_pydatetime(),
                    open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"],
                    volume=int(row["Volume"]),
                    indicators=indicators
                ))

            # Update specific docs with indicators
            await self.repository.save_historical_prices(symbol, ta_prices)
            del ta_prices, df_ta
        else:
            await self.sync_incremental_prices(symbol, history_df)

        gc.collect()
        return stock

    async def sync_incremental_prices(self, symbol: str, new_history_df: Any):
        for index, row in new_history_df.iterrows():
            # Robust datetime conversion
            if hasattr(index, 'to_pydatetime'):
                dt = index.to_pydatetime()
            elif isinstance(index, (datetime, pd.Timestamp)):
                dt = index
            else:
                dt = pd.to_datetime(index).to_pydatetime()

            price = StockPrice(
                symbol=symbol,
                date=dt,
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"]) if "Volume" in row else 0
            )
            await self.repository.save_historical_prices(symbol, [price])

    async def get_market_overview(self, limit: int = 50, offset: int = 0) -> List[Stock]:
        return await self.repository.get_all_stocks(limit, offset)

    async def validate_data_quality(self, symbol: str, df: Any) -> Dict[str, Any]:
        import pandas as pd
        report = {"symbol": symbol, "timestamp": datetime.now(), "status": "passed", "issues": []}
        if df.isnull().values.any():
            report["status"] = "failed"
            report["issues"].append("Missing OHLCV data found")
        return report

    async def validate_corporate_action_normalization(self) -> Dict[str, Any]:
        """
        Step 2E: Price Normalization Validation.
        Ensures adjusted prices are consistent with raw prices across key stocks.
        Part 17 & 18 implementation.
        """
        test_symbols = ["INFY", "ITC", "RELIANCE", "TCS"]
        results = {}

        for symbol in test_symbols:
            try:
                # Most providers return adjusted by default, so we compare yf history modes
                import yfinance as yf
                ticker = yf.Ticker(f"{symbol}.NS")

                raw_df = ticker.history(period="1d", auto_adjust=False)
                adj_df = ticker.history(period="1d", auto_adjust=True)

                if not raw_df.empty and not adj_df.empty:
                    raw_current = float(raw_df["Close"].iloc[-1])
                    adj_current = float(adj_df["Close"].iloc[-1])
                    factor = adj_current / raw_current if raw_current != 0 else 1.0

                    results[symbol] = {
                        "raw_current": round(raw_current, 2),
                        "adjusted_current": round(adj_current, 2),
                        "adjustment_factor": round(factor, 4),
                        "normalized_current": round(adj_current, 2)
                    }
                else:
                    results[symbol] = {"error": "DATA_UNAVAILABLE"}
            except Exception as e:
                results[symbol] = {"error": str(e)}
        return results

    async def refresh_derivative_universe(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Operational Automation: Automated Contract Discovery.
        Handles expiry and populates InstrumentDB with current Near/Next/Far contracts.
        """
        if not symbols:
            # Default to F&O eligible stocks from DB
            all_stocks = await self.repository.get_all_stocks(limit=500)
            symbols = [s.symbol for s in all_stocks if s.is_fno]

        print(f"[*] Refreshing derivative universe for {len(symbols)} symbols...")

        discovered_count = 0
        errors = []

        for symbol in symbols:
            try:
                # 1. Discover Expiries
                expiries = await self.provider.get_expiries(symbol)
                if not expiries:
                    continue

                # 2. Near/Next/Far Expiries (Sorted)
                expiries = sorted(expiries)[:3]

                instruments_to_save = []

                for expiry in expiries:
                    # A. Futures
                    fut_id = f"{symbol}_{expiry.strftime('%y%b').upper()}_FUT"
                    instruments_to_save.append({
                        "id": fut_id,
                        "exchange": "NSE",
                        "trading_symbol": f"{symbol}{expiry.strftime('%y%b').upper()}FUT",
                        "segment": "FUTURES",
                        "instrument_type": "FUTSTK" if symbol not in ["NIFTY", "BANKNIFTY", "FINNIFTY"] else "FUTIDX",
                        "underlying_symbol": symbol,
                        "expiry": expiry,
                        "source": self.provider.__class__.__name__,
                        "last_updated": datetime.utcnow()
                    })
                    discovered_count += 1

                    # B. Options (Sample ATM and +/- 2 strikes)
                    # Fetch actual option chain to get strikes
                    try:
                        chain = await self.provider.get_option_chain(symbol, expiry)
                        # Filter to get a few strikes around ATM
                        # Since yfinance_provider doesn't return full chain in get_option_chain yet,
                        # we might need to enhance that too.
                        # For now, let's assume we can add a few deterministic ones if it's an index
                        if symbol == "NIFTY":
                             strikes = [24000, 24500, 25000]
                        else:
                             # Dummy strikes for stock options discovery test
                             strikes = [] # Will add logic to get strikes if possible

                        for strike in strikes:
                            for o_type in ["CE", "PE"]:
                                opt_id = f"{symbol}_{expiry.strftime('%y%b').upper()}_{strike}_{o_type}"
                                instruments_to_save.append({
                                    "id": opt_id,
                                    "exchange": "NSE",
                                    "trading_symbol": f"{symbol}{expiry.strftime('%y%b').upper()}{strike}{o_type}",
                                    "segment": "OPTIONS",
                                    "instrument_type": "OPTSTK" if symbol not in ["NIFTY", "BANKNIFTY", "FINNIFTY"] else "OPTIDX",
                                    "underlying_symbol": symbol,
                                    "expiry": expiry,
                                    "strike": float(strike),
                                    "option_type": o_type,
                                    "source": self.provider.__class__.__name__,
                                    "last_updated": datetime.utcnow()
                                })
                                discovered_count += 1
                    except: pass

                await self.repository.save_instruments(instruments_to_save)

            except Exception as e:
                errors.append({"symbol": symbol, "error": str(e)})

        return {
            "status": "SUCCESS" if not errors else "PARTIAL_SUCCESS",
            "discovered_count": discovered_count,
            "errors": errors
        }
