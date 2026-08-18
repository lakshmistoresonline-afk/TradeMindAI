
import os
import sys
import json
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def run_feature_audit():
    print("--- FEATURE QUALITY AUDIT ---")

    # 1. Inspect Feature Definitions
    defs = await container.data_platform_repo.get_feature_definitions()
    print(f"Total defined features: {len(defs)}")

    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    audit_results = []

    for symbol in symbols:
        # Fetch features from analytical store (DuckDB)
        features = await container.data_platform_repo.get_features_by_range(
            symbol,
            datetime.datetime(2023, 1, 1),
            datetime.datetime.now()
        )

        if not features:
            print(f"[!] No features found for {symbol}")
            continue

        df = pd.DataFrame([f.features for f in features])

        for col in df.columns:
            missing_rate = df[col].isnull().mean()
            constant_rate = (df[col] == df[col].iloc[0]).mean() if len(df) > 0 else 1.0

            # Predictiveness (Simplified: Correlation with 5-day forward return)
            # This requires fetching price data and aligning

            audit_results.append({
                "symbol": symbol,
                "feature": col,
                "missing_rate": missing_rate,
                "constant_rate": constant_rate,
                "source": "Analytical Engine (DuckDB)"
            })

    audit_df = pd.DataFrame(audit_results)

    # Aggregate by feature
    summary = audit_df.groupby('feature').agg({
        'missing_rate': 'mean',
        'constant_rate': 'mean'
    })

    print("\n[Feature Summary]")
    print(summary)

    # Save results
    os.makedirs("validation/feature_audit", exist_ok=True)
    summary.to_markdown("validation/feature_audit/FEATURE_AUDIT.md")
    summary.to_json("validation/feature_audit/feature_quality.json")

if __name__ == "__main__":
    import asyncio
    import datetime
    asyncio.run(run_feature_audit())
