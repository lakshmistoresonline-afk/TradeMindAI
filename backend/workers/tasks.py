from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings
from backend.core.database import db_client
from backend.data.collector import DataCollector
from backend.analysis.technical import TechnicalAnalysis
from backend.ai.workflow import create_ai_workflow
import datetime

from backend.analysis.smc import SMCAnalysis
from backend.analysis.backtester import BacktestEngine

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
}
celery_app.conf.timezone = 'Asia/Kolkata'

@celery_app.task
def analyze_stock_task(symbol: str, period="10y"):
    # Use the global db_client for Firestore
    db = db_client
    try:
        collector = DataCollector(db)
        # 1. Fetch data
        collector.fetch_stock_info(symbol)
        df = collector.fetch_historical_data(symbol, period=period)

        if df.empty:
            return f"No data found for {symbol}"

        # 2. Technical & SMC Analysis
        df_ta = TechnicalAnalysis.calculate_indicators(df)
        last_ta = df_ta.iloc[-1].to_dict()

        smc_obs = SMCAnalysis.detect_order_blocks(df)
        smc_fvgs = SMCAnalysis.detect_fvg(df)

        # 3. AI Consensus
        workflow = create_ai_workflow()
        initial_state = {
            "symbol": symbol,
            "technical_data": {
                "indicators": last_ta,
                "smc": {
                    "order_blocks": smc_obs[-5:], # Last 5 OBs
                    "fvgs": smc_fvgs[-5:] # Last 5 FVGs
                }
            },
            "fundamental_data": {},
            "news_sentiment": {},
            "recommendations": [],
            "consensus": ""
        }
        result = workflow.invoke(initial_state)

        # Update Firestore with detailed analysis
        db.collection("stocks").document(symbol).update({
            "analysis": result,
            "updated_at": datetime.datetime.utcnow()
        })

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

    for symbol in symbols:
        analyze_stock_task.delay(symbol, period=period)

    return f"Automated analysis triggered for the complete Nifty 50 list with {period} history."

@celery_app.task
def run_adhoc_backtest(symbol: str):
    db = db_client
    engine = BacktestEngine(db)
    return engine.run_10y_backtest(symbol)
