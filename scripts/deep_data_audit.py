import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, StockDB, PriceDB, NewsDB, EarningsDB
from scripts.audit_database import NIFTY_100

def deep_audit():
    session = SessionLocal()
    print("--- TRADEMIND AI: DEEP DATA FIDELITY AUDIT ---")

    # 1. AI Status Audit
    ai_status = session.query(StockDB.ai_status, text("count(*)")).group_by(StockDB.ai_status).all()
    print(f"\n1. AI Consensus Status: {dict(ai_status)}")

    # 2. News Coverage Audit
    news_counts = session.query(NewsDB.symbol, text("count(*)")).group_by(NewsDB.symbol).all()
    stocks_with_news = len(news_counts)
    total_news = sum(c[1] for c in news_counts)
    print(f"2. News Coverage: {stocks_with_news}/129 stocks have news (Total headlines: {total_news})")

    # 3. Options Availability
    stocks = session.query(StockDB).all()
    with_options = [s.symbol for s in stocks if s.options_data and s.options_data.get('available') != False]
    print(f"3. Options Data: {len(with_options)}/129 stocks have active option chains.")

    # 4. Earnings Availability
    earnings_count = session.query(EarningsDB.symbol, text("count(*)")).group_by(EarningsDB.symbol).all()
    print(f"4. Earnings Data: {len(earnings_count)}/129 stocks have calendar/results data.")

    # 5. Missing Fundamentals Audit
    missing_pe = [s.symbol for s in stocks if not s.pe_ratio or s.pe_ratio == 0]
    print(f"5. Fundamental Gaps: {len(missing_pe)} stocks missing PE ratios.")

    # 6. Failed AI Traces
    failed = session.query(StockDB).filter(StockDB.ai_status == "FAILED").all()
    print(f"6. AI Failures: {len(failed)} found.")
    for f in failed[:5]:
        print(f"   - {f.symbol}: {f.ai_last_error[:100]}...")

    session.close()

if __name__ == "__main__":
    deep_audit()
