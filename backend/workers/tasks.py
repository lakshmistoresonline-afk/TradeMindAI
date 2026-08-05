from celery import Celery, group
from celery.schedules import crontab
from backend.core.config import settings
from backend.core.database import db_client
from backend.data.collector import DataCollector
from backend.analysis.technical import TechnicalAnalysis
from backend.ai.workflow import create_ai_workflow
import datetime

from backend.analysis.smc import SMCAnalysis
from backend.analysis.backtester import BacktestEngine
from backend.services.quant_engine import QuantEngine

celery_app = Celery("tasks", broker=settings.REDIS_URL)

# Automated Schedule
celery_app.conf.beat_schedule = {
    "analyze-nifty-50-morning": {
        "task": "backend.workers.tasks.analyze_nifty_50",
        "schedule": crontab(hour=9, minute=30, day_of_week="mon-fri"),
    },
    "analyze-nifty-50-evening": {
        "task": "backend.workers.tasks.analyze_nifty_50",
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
        ai_features = feature_store.extract_ai_features(df_ta, smc_data)
        await feature_store.ingest_features(symbol, df.index[-1], ai_features)

        # 5. Quantitative Analytics (Institutional Metrics)
        nifty_df = await service.provider.fetch_history("^NSEI", period)
        quant_metrics = QuantEngine.calculate_metrics(symbol, df, nifty_df)

        # 6. ML Prediction (Using champion model)
        ml_prediction = await ml_service.predict_with_champion(symbol, ai_features)

        # 7. AI Consensus (Reading from Precomputed Features)
        workflow = create_ai_workflow()
        initial_state = {
            "symbol": symbol,
            "technical_data": {
                "indicators": ai_features,
                "smc": smc_data,
                "ml_prediction": ml_prediction,
                "quant_metrics": quant_metrics.model_dump()
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

        # 7. Persist Global Source of Truth
        await service.repository.update_analysis(symbol, result)

        # 8. Broadcast Real-time Alert (Enterprise Integration)
        from backend.app.main import manager
        alert_msg = {
            "type": "ANALYSIS_COMPLETE",
            "symbol": symbol,
            "signal": result.get("consensus", "HOLD")[:50],
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        await manager.broadcast(json.dumps(alert_msg))

        return result["consensus"]
    except Exception as e:
        return f"Error analyzing {symbol}: {str(e)}"

@celery_app.task
def analyze_nifty_50(period="10y"):
    # Official Nifty 50 symbols (updated for NSE)
    symbols = [
        "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
        "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL",
        "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT",
        "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
        "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC", "INDUSINDBK",
        "INFY", "JSWSTEEL", "KOTAKBANK", "LT", "LTIM",
        "M&M", "MARUTI", "NTPC", "NESTLEIND", "ONGC",
        "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
        "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS", "TECHM",
        "TITAN", "ULTRACEMCO", "UPL", "WIPRO", "SHRIRAMFIN"
    ]

    # Use Celery group for parallel execution
    job = group(analyze_stock_task.s(symbol, period=period) for symbol in symbols)
    job.apply_async()

    return f"Parallel analysis triggered for {len(symbols)} stocks."

@celery_app.task
def run_adhoc_backtest(symbol: str):
    db = db_client
    engine = BacktestEngine(db)
    return engine.run_10y_backtest(symbol)

@celery_app.task
def train_models_task():
    """
    Retrains models for all Nifty 50 stocks using the Feature Store.
    """
    service = container.stock_service
    ml_service = container.ml_service

    symbols = [
        "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
        "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL",
        "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT",
        "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
        "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC", "INDUSINDBK",
        "INFY", "JSWSTEEL", "KOTAKBANK", "LT", "LTIM",
        "M&M", "MARUTI", "NTPC", "NESTLEIND", "ONGC",
        "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
        "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS", "TECHM",
        "TITAN", "ULTRACEMCO", "UPL", "WIPRO", "SHRIRAMFIN"
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
