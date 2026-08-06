from celery import Celery, group
from celery.schedules import crontab
from backend.core.config import settings
from backend.core.database import db_client
import datetime
import yfinance as yf
import json

celery_app = Celery("tasks", broker=settings.REDIS_URL)

# Automated Schedule
celery_app.conf.beat_schedule = {
    "analyze-nifty-100-morning": {
        "task": "backend.workers.tasks.analyze_nifty_100",
        "schedule": crontab(hour=9, minute=30, day_of_week="mon-fri"),
    },
    "analyze-nifty-100-evening": {
        "task": "backend.workers.tasks.analyze_nifty_100",
        "schedule": crontab(hour=16, minute=0, day_of_week="mon-fri"),
    },
    "retrain-models-weekly": {
        "task": "backend.workers.tasks.train_models_task",
        "schedule": crontab(hour=10, minute=0, day_of_week="sat"),
    },
    "generate-labels-daily": {
        "task": "backend.workers.tasks.update_training_labels",
        "schedule": crontab(hour=18, minute=0, day_of_week="mon-fri"),
    },
    "market-intel-closing": {
        "task": "backend.workers.tasks.process_market_intelligence",
        "schedule": crontab(hour=16, minute=30, day_of_week="mon-fri"),
    },
    "refresh-rankings-daily": {
        "task": "backend.workers.tasks.refresh_ai_rankings",
        "schedule": crontab(hour=17, minute=0, day_of_week="mon-fri"),
    },
}
celery_app.conf.timezone = 'Asia/Kolkata'

from backend.core.container import container
import asyncio

@celery_app.task
def analyze_stock_task(symbol: str, period="10y"):
    # Wrapper to run async service in sync celery
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_analyze_stock_logic(symbol, period))

async def _analyze_stock_logic(symbol: str, period: str):
    import pandas as pd
    from backend.analysis.technical import TechnicalAnalysis
    from backend.ai.workflow import create_ai_workflow
    from backend.analysis.smc import SMCAnalysis
    from backend.services.quant_engine import QuantEngine
    from backend.services.scoring_service import ScoringService

    # Diagnostic Log
    container.repository.db.collection("system_logs").add({
        "type": "WORKER_START",
        "symbol": symbol,
        "timestamp": datetime.datetime.utcnow()
    })

    service = container.stock_service
    ml_service = container.ml_service
    feature_store = container.feature_store

    # Ensure feature registry is initialized
    await feature_store.initialize_registry()

    try:
        # 1. Incremental Sync
        stock = await service.collect_stock_data(symbol, period)

        # 2. Get Context (250 bars)
        recent_prices = await service.repository.get_recent_prices(symbol, limit=250)
        if not recent_prices:
            return f"No price history found for {symbol}"

        df = pd.DataFrame([p.model_dump() for p in recent_prices])
        df.set_index('date', inplace=True)

        # Data Quality Check
        quality_report = await service.validate_data_quality(symbol, df)
        if quality_report["status"] == "failed":
            print(f"Data Quality Warning for {symbol}: {quality_report['issues']}")

        # 3. Technical & SMC Analysis
        df_ta = TechnicalAnalysis.calculate_indicators(df)
        smc_obs = SMCAnalysis.detect_order_blocks(df)
        smc_fvgs = SMCAnalysis.detect_fvg(df)

        smc_data = {
            "order_blocks": smc_obs[-5:],
            "fvgs": smc_fvgs[-5:]
        }

        # 4. Feature Store Ingestion (Standardized AI Inputs)
        ai_features = feature_store.extract_institutional_features(df_ta, smc_data)
        await feature_store.ingest_features(symbol, df.index[-1], ai_features)

        # 5. Quantitative Analytics (Institutional Metrics)
        nifty_df = await service.provider.fetch_history("^NSEI", period)
        quant_metrics = QuantEngine.calculate_metrics(symbol, df, nifty_df)

        # 6. ML Prediction (Using champion model)
        ml_prediction = await ml_service.predict_with_champion(symbol, ai_features)

        # 7. AI Consensus (Reading from Precomputed Features)
        workflow = create_ai_workflow()

        # Vision 2.0: Multi-Timeframe Alignment
        mtf_results = await container.timeframe_service.analyze_alignment(symbol)

        initial_state = {
            "symbol": symbol,
            "technical_data": {
                "indicators": ai_features,
                "smc": smc_data,
                "ml_prediction": ml_prediction,
                "quant_metrics": quant_metrics.model_dump(),
                "mtf_alignment": mtf_results
            },
            "fundamental_data": {
                "pe_ratio": stock.pe_ratio,
                "pb_ratio": stock.pb_ratio,
                "market_cap": stock.market_cap
            },
            "news_sentiment": {},
            "recommendations": [],
            "consensus": ""
        }
        result = workflow.invoke(initial_state)

        # 8. Unified AI Investment Score
        scoring_results = ScoringService.calculate_unified_score(ai_features, ml_prediction, result)

        # 9. Persist Global Source of Truth
        await service.repository.db.collection("stocks").document(symbol).update({
            "analysis": result,
            "ai_investment_score": scoring_results["score"],
            "ai_investment_grade": scoring_results["grade"],
            "health_metrics": scoring_results["health"],
            "confidence_metrics": scoring_results["confidence"],
            "updated_at": datetime.datetime.utcnow()
        })

        # Diagnostic Log
        container.repository.db.collection("system_logs").add({
            "type": "WORKER_SUCCESS",
            "symbol": symbol,
            "timestamp": datetime.datetime.utcnow(),
            "consensus": result.get("consensus", "HOLD")[:50]
        })

        return result["consensus"]
    except Exception as e:
        # Error Log
        container.repository.db.collection("system_logs").add({
            "type": "WORKER_ERROR",
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.datetime.utcnow()
        })
        return f"Error analyzing {symbol}: {str(e)}"

@celery_app.task
def analyze_nifty_100(period="10y"):
    # Official Nifty 100 symbols (updated for NSE)
    symbols = [
        "ABB", "ACC", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL", "AMBUJACEM", "APOLLOHOSP",
        "ASHOKLEY", "ASIANPAINT", "ASTRAL", "AU SMALL FINANCE BANK", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BALKRISIND",
        "BANDHANBNK", "BANKBARODA", "BANKINDIA", "BEL", "BHEL", "BPCL", "BHARTIARTL", "BIOCON", "BOSCHLTD", "BRITANNIA",
        "CANBK", "CGPOWER", "CHOLAFIN", "CIPLA", "COALINDIA", "COLPAL", "CONCOR", "CUMMINSIND", "DLF", "DABUR",
        "DALBHARAT", "DEEPAKNTR", "DRREDDY", "EICHERMOT", "ESCORTS", "GAIL", "GMRINFRA", "GLAND", "GODREJCP", "GODREJPROP",
        "GRASIM", "GUJGASLTD", "HAL", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO", "HINDUNILVR",
        "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDFCFIRSTB", "ITC", "INDHOTEL", "INDIANB", "INDUSINDBK", "INDUSTOWER", "INFY",
        "INTERGLOBE", "IOC", "IRCTC", "IRFC", "JSWENERGY", "JSWSTEEL", "JINDALSTEL", "JUBLFOOD", "KOTAKBANK", "LTIM",
        "LT", "LICHSGFIN", "LICI", "MRF", "M&M", "MARICO", "MARUTI", "MAXHEALTH", "MAHABANK", "MPHASIS",
        "NHPC", "NMDC", "NTPC", "NESTLEIND", "NYKAA", "ONGC", "PAYTM", "PIIND", "PNB", "PFC",
        "PAGEIND", "PATANJALI", "PIDILITIND", "POLYCAB", "POWERGRID", "PRESTIGE", "RVNL", "RECLTD", "RELIANCE", "SBICARD",
        "SBILIFE", "SBIN", "SRF", "SAMVARDHANA", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SONACOMS", "SUNPHARMA", "SUNTV",
        "SUPREMEIND", "SYNGENE", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAMTRDVR", "TATAPOWER", "TATASTEEL", "TCS", "TECHM",
        "TITAN", "TORNTPHARM", "TRENT", "TIINDIA", "UPL", "ULTRACEMCO", "UNITDSPR", "VBL", "VEDL", "WIPRO",
        "YESBANK", "ZOMATO", "ZYDUSLIFE"
    ]

    # Use Celery group for parallel execution
    job = group(analyze_stock_task.s(symbol, period=period) for symbol in symbols)
    job.apply_async()

    return f"Parallel analysis triggered for {len(symbols)} stocks."

@celery_app.task
def run_adhoc_backtest(symbol: str):
    from backend.analysis.backtester import BacktestEngine
    db = db_client
    engine = BacktestEngine(db)
    return engine.run_10y_backtest(symbol)

@celery_app.task
def train_models_task():
    """
    Retrains models for all Nifty 100 stocks using the Feature Store.
    """
    service = container.stock_service
    ml_service = container.ml_service

    symbols = [
        "ABB", "ACC", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL", "AMBUJACEM", "APOLLOHOSP",
        "ASHOKLEY", "ASIANPAINT", "ASTRAL", "AUBANK", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BALKRISIND",
        "BANDHANBNK", "BANKBARODA", "BEL", "BHEL", "BPCL", "BHARTIARTL", "BIOCON", "BOSCHLTD", "BRITANNIA", "CANBK",
        "CGPOWER", "CHOLAFIN", "CIPLA", "COALINDIA", "COLPAL", "CONCOR", "CUMMINSIND", "DLF", "DABUR", "DALBHARAT",
        "DEEPAKNTR", "DRREDDY", "EICHERMOT", "GAIL", "GMRINFRA", "GODREJCP", "GODREJPROP", "GRASIM", "HAL", "HCLTECH",
        "HDFCBANK", "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDFCFIRSTB",
        "ITC", "INDHOTEL", "INDIANB", "INDUSINDBK", "INDUSTOWER", "INFY", "INTERGLOBE", "IOC", "IRCTC", "IRFC",
        "JSWENERGY", "JSWSTEEL", "JINDALSTEL", "JUBLFOOD", "KOTAKBANK", "LTIM", "LT", "LICHSGFIN", "LICI", "MRF",
        "M&M", "MARICO", "MARUTI", "MAXHEALTH", "MPHASIS", "NHPC", "NMDC", "NTPC", "NESTLEIND", "NYKAA",
        "ONGC", "PAYTM", "PIIND", "PNB", "PFC", "PIDILITIND", "POLYCAB", "POWERGRID", "PRESTIGE", "RVNL",
        "RECLTD", "RELIANCE", "SBICARD", "SBILIFE", "SBIN", "SRF", "MOTHERSON", "SHREECEM", "SHRIRAMFIN", "SIEMENS",
        "SONACOMS", "SUNPHARMA", "SUNTV", "SUPREMEIND", "SYNGENE", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL",
        "TCS", "TECHM", "TITAN", "TORNTPHARM", "TRENT", "TIINDIA", "UPL", "ULTRACEMCO", "UNITDSPR", "VBL",
        "VEDL", "WIPRO", "YESBANK", "ZOMATO", "ZYDUSLIFE"
    ]

    loop = asyncio.get_event_loop()
    for symbol in symbols:
        loop.run_until_complete(_train_with_features(symbol, ml_service))

    return f"Retraining complete for {len(symbols)} stocks."

async def _train_with_features(symbol, ml_service):
    # Fetch all features with targets from Feature Store
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=365*5) # 5 years
    features = await container.data_platform_repo.get_features_by_range(symbol, start_date, end_date)

    if features:
        await ml_service.train_and_register(symbol, features)

@celery_app.task
def update_training_labels():
    """
    Daily task to update Feature Store with actual price outcomes.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_update_labels_logic())

@celery_app.task
def process_market_intelligence():
    """
    Vision 2.0: Generates Daily Intelligence, Regimes, and Opportunities.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_intel_logic())

@celery_app.task
def refresh_ai_rankings():
    """
    Vision 2.0: AI Ranking Engine (Module 13).
    Recalculates top picks across categories.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_refresh_rankings_logic())

async def _process_intel_logic():
    service = container.stock_service
    ios_repo = container.ios_repo

    # 1. Fetch Latest Market State
    stocks = await service.repository.get_all_stocks(limit=100)

    # Replicate market stats logic to avoid circular import from endpoints
    indices = {"^NSEI": "NIFTY 50", "^CNX100": "NIFTY 100", "^NSEBANK": "BANK NIFTY", "^INDIAVIX": "India VIX"}
    stats = {}
    for symbol, name in indices.items():
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        stats[name] = {
            "value": round(info.last_price, 2),
            "change": round(((info.last_price - info.previous_close) / info.previous_close) * 100, 2)
        }

    # 2. Detect Market Regime
    nifty_df = await service.provider.fetch_history("^NSEI", "1mo")
    vix_data = stats.get("India VIX", {}).get("value", 15.0)
    regime = container.regime_engine.detect_regime(nifty_df, vix_data)
    await ios_repo.save_market_regime(regime)

    # 3. Find Opportunities
    opportunities = container.opportunity_engine.find_opportunities(stocks)
    for opp in opportunities:
        await ios_repo.save_opportunity(opp)

    # 4. Generate Closing Report
    report = container.intel_service.generate_closing_report(stocks, stats)
    await ios_repo.save_intel_report(report)

    return "Market Intelligence Processed."

async def _refresh_rankings_logic():
    service = container.stock_service
    repo = service.repository

    # 1. Fetch All Analyzed Stocks
    stocks = await repo.get_all_stocks(limit=100)

    # 2. Category Ranking
    top_ai = sorted([s for s in stocks if s.ai_investment_score], key=lambda x: x.ai_investment_score, reverse=True)[:10]
    top_momentum = sorted([s for s in stocks if s.change_pct], key=lambda x: x.change_pct, reverse=True)[:10]

    # 3. Save to Global Ranking Collection
    db = repo.db
    ranking_ref = db.collection("system_rankings").document("latest")
    ranking_ref.set({
        "top_ai_confidence": [{"symbol": s.symbol, "score": s.ai_investment_score} for s in top_ai],
        "top_momentum": [{"symbol": s.symbol, "change": s.change_pct} for s in top_momentum],
        "updated_at": datetime.datetime.utcnow()
    })

    return "AI Rankings Refreshed."

async def _update_labels_logic():
    repo = container.repository
    dp_repo = container.data_platform_repo

    # We look for features 5-10 days ago that don't have targets yet
    check_date = datetime.datetime.utcnow() - datetime.timedelta(days=5)

    # Get all analyzed stocks
    stocks = await repo.get_all_stocks()
    for stock in stocks:
        # Get historical prices to find the outcome
        prices = await repo.get_recent_prices(stock.symbol, limit=20)
        # Find features near check_date
        features = await dp_repo.get_features_by_range(stock.symbol, check_date - datetime.timedelta(days=1), check_date + datetime.timedelta(days=1))

        for feat in features:
            if feat.target is None:
                # Find price at feat.date and feat.date + 5 trading days
                # Simplified: compare feat price to current price if 5 days passed
                entry_price = [p.close for p in prices if p.date.date() == feat.date.date()]
                current_price = stock.last_price

                if entry_price and current_price:
                    feat.target = 1.0 if current_price > entry_price[0] else 0.0
                    await dp_repo.save_feature_vector(feat)

    return "Training labels updated."
