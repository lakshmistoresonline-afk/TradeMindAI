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

                    # RC-3: High-Fidelity Forensic Audit Logic
                    # 1. Extract what the AI suggested back then
                    structured = {}
                    try:
                        import re, json
                        json_match = re.search(r'(\{.*\})', ai_result["consensus"], re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1).replace("'", "\"")
                            structured = json.loads(json_str)
                    except: pass

                    entry_price = df["Close"].iloc[i]
                    target_price = structured.get("target", entry_price * 1.1)
                    stop_loss_price = structured.get("stop_loss", entry_price * 0.95)

                    # 2. Simulate price action for the next 30 bars
                    outcome = "EXPIRED"
                    exit_price = df["Close"].iloc[i + 30]
                    hit_date = current_df.index[-1]

                    future_df = df.iloc[i+1 : i+31]
                    for f_date, row in future_df.iterrows():
                        if row["High"] >= target_price:
                            outcome = "TARGET_HIT"
                            exit_price = target_price
                            hit_date = f_date
                            break
                        if row["Low"] <= stop_loss_price:
                            outcome = "STOP_LOSS"
                            exit_price = stop_loss_price
                            hit_date = f_date
                            break

                    is_success = outcome == "TARGET_HIT"
                    if is_success:
                        success_signals += 1

                    results.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "signal": "BUY",
                        "entry": round(float(entry_price), 2),
                        "target": round(float(target_price), 2),
                        "stop_loss": round(float(stop_loss_price), 2),
                        "exit_price": round(float(exit_price), 2),
                        "hit_date": hit_date.strftime("%Y-%m-%d"),
                        "profit_pct": round(((exit_price - entry_price) / entry_price) * 100, 2),
                        "outcome": outcome,
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
