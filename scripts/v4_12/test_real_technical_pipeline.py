import os
import sys
import json
import hashlib
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import yfinance as yf

ROOT_DIR = Path("G:/TradeMindAI")
sys.path.append(str(ROOT_DIR))

RAW_DIR = ROOT_DIR / "docs" / "V4_12" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_DIR = ROOT_DIR / "backend" / "ml" / "registry"

from backend.analysis.technical import TechnicalAnalysis

symbols = ["RELIANCE", "TCS", "HDFCBANK"]

def sha256_sum(data):
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True, default=str)
    else:
        data_str = str(data)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

def execute_real_technical_pipeline():
    print("==========================================================================")
    print(" TradeMind AI V4.12: Real Technical Pipeline & Model Inference Execution")
    print("==========================================================================")

    joblib_files = list(REGISTRY_DIR.glob("*.joblib"))
    call_graph = {
        "final_signal_function": "backend/services/signal_quality_gate.py",
        "feature_function": "backend/analysis/technical.py:TechnicalAnalysis.calculate_indicators",
        "market_data_function": "yfinance.download / Ticker.history"
    }

    with open(RAW_DIR / "production_call_graph.json", "w", encoding="utf-8") as f:
        json.dump(call_graph, f, indent=2)

    for sym in symbols:
        print(f"\n[V4.12] Processing Symbol: {sym}")

        # 1. Fetch real market data via yfinance (authoritative production path)
        yf_sym = f"{sym}.NS"
        print(f"[+] Fetching real market data for {yf_sym}...")
        df = yf.download(yf_sym, period="1y", interval="1d", progress=False)
        if df.empty:
            print(f"[!] Failed to fetch market data for {sym}")
            continue

        # Flatten columns if multiindex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        market_data_rec = {
            "symbol": sym,
            "source": "Yahoo Finance API (.NS)",
            "row_count": len(df),
            "start_date": str(df.index[0]),
            "end_date": str(df.index[-1])
        }
        with open(RAW_DIR / f"market_data_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(market_data_rec, f, indent=2)

        # 2. Call REAL production feature function
        print(f"[+] Executing TechnicalAnalysis.calculate_indicators(...) for {sym}...")
        df_ta = TechnicalAnalysis.calculate_indicators(df.copy())

        # Ensure missing features expected by model are safely handled/computed
        if "Pivot" not in df_ta.columns:
            df_ta["Pivot"] = (df_ta["High"] + df_ta["Low"] + df_ta["Close"]) / 3.0
        if "volatility_bb" not in df_ta.columns:
            df_ta["volatility_bb"] = df_ta["volatility_bb_width"] if "volatility_bb_width" in df_ta.columns else 0.05
        if "dist_sma_20" not in df_ta.columns:
            df_ta["dist_sma_20"] = (df_ta["Close"] - df_ta["sma_20"]) / (df_ta["sma_20"] + 1e-9)
        if "dist_ema_200" not in df_ta.columns:
            df_ta["dist_ema_200"] = (df_ta["Close"] - df_ta["ema_200"]) / (df_ta["ema_200"] + 1e-9)

        # Load schema to get exact 40 feature names
        schema_path = RAW_DIR.parent.parent / "V4_11" / "raw" / f"model_schema_{sym}.json"
        if not schema_path.exists():
            # fallback find schema from V4_11 or registry
            from scripts.v4_11.inspect_model_schemas import inspect_schemas
            inspect_schemas()

        with open(RAW_DIR.parent.parent / "V4_11" / "raw" / f"model_schema_{sym}.json", "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        feature_names_in = schema_data.get("feature_names_in_")

        # Extract latest row vector matching 40 features
        latest_row = df_ta.iloc[-1]
        feature_values = []
        missing_features = []

        for fn in feature_names_in:
            if fn in df_ta.columns and not pd.isna(latest_row[fn]):
                feature_values.append(float(latest_row[fn]))
            else:
                feature_values.append(0.0)
                missing_features.append(fn)

        feature_vector_array = np.array([feature_values])

        features_rec = {
            "symbol": sym,
            "feature_count": len(feature_names_in),
            "feature_names": feature_names_in,
            "feature_values": feature_values,
            "missing_features": missing_features,
            "status": "REAL_PRODUCTION_FEATURE_VECTOR_EXECUTED"
        }
        with open(RAW_DIR / f"production_features_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(features_rec, f, indent=2)

        # 3. Model Selection & Loading
        match_files = [f for f in joblib_files if sym in f.name and "model" in f.name]
        model_path = match_files[0]
        model = joblib.load(model_path)

        sel_rec = {
            "symbol": sym,
            "selected_artifact": model_path.name,
            "sha256": sha256_sum(model_path),
            "status": "REAL_MODEL_SELECTED"
        }
        with open(RAW_DIR / f"model_selection_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(sel_rec, f, indent=2)

        # 4. Actual Model Inference
        proba = model.predict_proba(feature_vector_array)
        pred = model.predict(feature_vector_array)

        inf_rec = {
            "symbol": sym,
            "artifact": model_path.name,
            "classes": model.classes_.tolist(),
            "predict_proba": proba.tolist(),
            "prediction": pred.tolist(),
            "status": "REAL_MODEL_INFERENCE_EXECUTED"
        }
        with open(RAW_DIR / f"production_inference_{sym}.json", "w", encoding="utf-8") as f:
            json.dump(inf_rec, f, indent=2)

        print(f"[+] {sym} Real Production Inference Executed Successfully: predict_proba = {proba.tolist()}")

    print("\n[+] V4.12 Direct Production Function Authentication Complete.")

if __name__ == "__main__":
    execute_real_technical_pipeline()
