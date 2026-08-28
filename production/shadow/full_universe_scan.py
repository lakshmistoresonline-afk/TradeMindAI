
import os
import sys
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def run_audit_scan():
    run_ts = datetime.utcnow()
    print(f"[*] Starting Full Universe Shadow Scan [{run_ts}]")

    csv_path = "validation/shadow/shadow_observations.csv"
    results = []

    for symbol in NIFTY_200_CONSTITUENTS:
        data = {
            "date": run_ts.date().isoformat(),
            "timestamp": run_ts.isoformat(),
            "symbol": symbol,
            "strategy_version": "v2.2",
            "model_version": None,
            "price": None,
            "probability": None,
            "calibrated_probability": None,
            "EV": None,
            "data_quality_score": 0.0,
            "liquidity": 0.0,
            "ATR": None,
            "EMA_200": None,
            "direction": None,
            "target": None,
            "stop": None,
            "decision": "NO_TRADE",
            "rejection_reason": None
        }

        try:
            # 1. Check Model
            champion = await container.data_platform_repo.get_champion_model(symbol)
            if not champion:
                data["decision"] = "NO_TRADE_MODEL_ERROR"
                data["rejection_reason"] = "NO_MODEL_FOUND"
            else:
                data["model_version"] = champion.version

                # 2. Check Data & Features
                features_list = await container.data_platform_repo.get_features_by_range(
                    symbol,
                    run_ts - timedelta(days=7),
                    run_ts
                )

                if not features_list:
                    data["decision"] = "DATA_UNAVAILABLE"
                    data["rejection_reason"] = "NO_FEATURES_FOUND"
                else:
                    last_f = features_list[-1]
                    last_features = last_f.features
                    last_date = last_f.date
                    data["EMA_200"] = last_features.get("ema_200")
                    data["ATR"] = last_features.get("volatility_bb") # Using BB as volatility proxy if ATR missing, but backfill uses ta.atr
                    # Backfill script uses: "volatility_bb", "market_volatility_z"
                    # Let's check technical.py: df["ATR"] = talib.volatility.average_true_range(...)
                    data["ATR"] = last_features.get("ATR")

                    # 3. Data Freshness Gate
                    if (run_ts - last_date).total_seconds() > 86400:
                        data["decision"] = "NO_TRADE_STALE_DATA"
                        data["rejection_reason"] = "STALE_MARKET_DATA"
                    else:
                        # 4. Liquidity Gate
                        stock = await container.repository.get_stock_by_symbol(symbol)
                        avg_vol = stock.avg_volume if stock and stock.avg_volume is not None else 0.0
                        data["liquidity"] = avg_vol
                        data["price"] = stock.last_price if stock else None

                        if avg_vol < 10_000_000:
                            data["decision"] = "NO_TRADE_LOW_LIQUIDITY"
                            data["rejection_reason"] = "INSUFFICIENT_LIQUIDITY"
                        else:
                            # 5. Full Signal Evaluation
                            ml_res = await container.ml_service.predict_with_champion(symbol, last_features)
                            data["probability"] = ml_res.get("metadata", {}).get("raw_probability_up")
                            data["calibrated_probability"] = ml_res.get("metadata", {}).get("calibrated_probability_up")

                            # Final Signal Engine Call for actual result
                            signal = await container.signal_engine.generate_signal(symbol, "EQUITY", "SWING")

                            if signal:
                                data["decision"] = "TRADE_SIGNAL"
                                data["EV"] = signal.expected_value
                                data["direction"] = signal.direction
                                data["target"] = signal.target_price
                                data["stop"] = signal.stop_loss_price
                                data["data_quality_score"] = signal.data_quality_score
                            else:
                                # Re-run logic for granular audit
                                direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
                                price = data["price"]
                                ema200 = data["EMA_200"]
                                if price is None or ema200 is None:
                                    data["decision"] = "NO_TRADE_DATA_ERROR"
                                    data["rejection_reason"] = "MISSING_PRICE_OR_EMA"
                                elif (direction == "LONG" and price < ema200) or (direction == "SHORT" and price > ema200):
                                    data["decision"] = "NO_TRADE_EMA_CONFLICT"
                                    data["rejection_reason"] = "TREND_CONFLICT"
                                elif ml_res.get("prediction") == "NEUTRAL":
                                    data["decision"] = "NO_TRADE_LOW_PROBABILITY"
                                    data["rejection_reason"] = "NEUTRAL_PREDICTION"
                                elif data["calibrated_probability"] and data["calibrated_probability"] < 0.52:
                                    data["decision"] = "NO_TRADE_LOW_PROBABILITY"
                                    data["rejection_reason"] = "WEAK_EDGE"
                                else:
                                    data["decision"] = "NO_TRADE_FILTERED"
                                    data["rejection_reason"] = "OTHER_FILTER"

        except Exception as e:
            data["decision"] = "NO_TRADE_DATA_ERROR"
            data["rejection_reason"] = f"EXCEPTION: {str(e)}"

        results.append(data)

    # Save to CSV (Append Mode)
    new_df = pd.DataFrame(results)
    header = not os.path.exists(csv_path)
    new_df.to_csv(csv_path, mode='a', index=False, header=header)

    print(f"[SUCCESS] Recorded {len(results)} evaluations to {csv_path}")

if __name__ == "__main__":
    asyncio.run(run_audit_scan())
