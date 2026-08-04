from celery import Celery
from backend.core.config import settings
from backend.core.database import db_client
from backend.data.collector import DataCollector
from backend.analysis.technical import TechnicalAnalysis
from backend.ai.workflow import create_ai_workflow

celery_app = Celery("tasks", broker=settings.REDIS_URL)

@celery_app.task
def analyze_stock_task(symbol: str):
    # Use the global db_client for Firestore
    db = db_client
    try:
        collector = DataCollector(db)
        # 1. Fetch data
        collector.fetch_stock_info(symbol)
        df = collector.fetch_historical_data(symbol)

        if df.empty:
            return f"No data found for {symbol}"

        # 2. Technical Analysis
        df_ta = TechnicalAnalysis.calculate_indicators(df)
        last_ta = df_ta.iloc[-1].to_dict()

        # 3. AI Consensus
        workflow = create_ai_workflow()
        initial_state = {
            "symbol": symbol,
            "technical_data": last_ta,
            "fundamental_data": {}, # Fetch from Firestore if needed
            "news_sentiment": {},
            "recommendations": [],
            "consensus": ""
        }
        result = workflow.invoke(initial_state)

        return result["consensus"]
    except Exception as e:
        return f"Error analyzing {symbol}: {str(e)}"
