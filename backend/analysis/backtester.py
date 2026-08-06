import datetime
from typing import Any
from google.cloud import firestore
from backend.ai.workflow import create_ai_workflow
from backend.analysis.technical import TechnicalAnalysis
from backend.analysis.smc import SMCAnalysis

class BacktestEngine:
    def __init__(self, db: firestore.Client):
        self.db = db
        self.workflow = create_ai_workflow()

    def run_10y_backtest(self, symbol: str):
        # 1. Load full 10y data from Firestore or YFinance (YFinance is more reliable for bulk)
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period="10y")

        if df.empty or len(df) < 250:
            return {"error": "Not enough data for 10y backtest"}

        results = []
        total_signals = 0
        success_signals = 0

        # 2. Step through in 7-day increments to save time/API costs
        # Start after 200 days to allow for EMA 200 calculation
        step = 7
        for i in range(200, len(df) - 30, step):
            # "Time Travel": AI only sees data up to current point i
            current_df = df.iloc[:i+1]
            current_date = current_df.index[-1]

            # Detect Patterns
            smc_obs = SMCAnalysis.detect_order_blocks(current_df)
            smc_fvgs = SMCAnalysis.detect_fvg(current_df)

            # Check if there's an interesting pattern to analyze (minimal effort optimization)
            # Only run AI if a Bullish Order Block or FVG was detected in the last 2 candles
            has_pattern = False
            if smc_obs and (i - smc_obs[-1]["index"]) <= 2 and smc_obs[-1]["type"] == "bullish":
                has_pattern = True
            if smc_fvgs and (i - smc_fvgs[-1]["index"]) <= 2 and smc_fvgs[-1]["type"] == "bullish":
                has_pattern = True

            if not has_pattern:
                continue

            # Run AI Analysis
            ta_indicators = TechnicalAnalysis.calculate_indicators(current_df).iloc[-1].to_dict()
            initial_state = {
                "symbol": symbol,
                "technical_data": {
                    "indicators": ta_indicators,
                    "smc": {"order_blocks": smc_obs[-3:], "fvgs": smc_fvgs[-3:]}
                },
                "fundamental_data": {},
                "news_sentiment": {},
                "recommendations": [],
                "consensus": ""
            }

            try:
                ai_result = self.workflow.invoke(initial_state)
                consensus = ai_result["consensus"].upper()

                if "BUY" in consensus:
                    total_signals += 1
                    # Measure accuracy: Check price after 30 days
                    entry_price = df["Close"].iloc[i]
                    exit_price = df["Close"].iloc[i + 30]

                    is_success = exit_price > entry_price
                    if is_success:
                        success_signals += 1

                    results.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "signal": "BUY",
                        "entry": entry_price,
                        "exit_30d": exit_price,
                        "profit_pct": ((exit_price - entry_price) / entry_price) * 100,
                        "success": is_success
                    })
            except Exception as e:
                print(f"Error in backtest at {current_date}: {e}")

        # 3. Store Final Report & Signals
        accuracy = (success_signals / total_signals * 100) if total_signals > 0 else 0
        report = {
            "symbol": symbol,
            "total_signals": total_signals,
            "success_rate": accuracy,
            "avg_profit": sum(r["profit_pct"] for r in results) / total_signals if total_signals > 0 else 0,
            "last_run": datetime.datetime.utcnow()
        }

        backtest_ref = self.db.collection("backtests").document(symbol)
        backtest_ref.set(report)

        # Store individual signals in a sub-collection for deep auditing
        signals_ref = backtest_ref.collection("signals")
        for res in results:
            signals_ref.document(res["date"]).set(res)

        return report
