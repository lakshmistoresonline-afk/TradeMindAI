import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def forensic_audit():
    print("============================================================")
    print(" QUANTITATIVE FORENSIC AUDIT - PROBABILITY TRACE")
    print("============================================================")

    with engine.connect() as conn:
        # 1. Stored Predictions Audit
        query = text("""
            SELECT symbol, date, model_version, prediction, confidence, metadata_json
            FROM predictions
            ORDER BY date DESC
            LIMIT 200
        """)
        df = pd.read_sql(query, conn)

        if df.empty:
            print("[!] No predictions found in database.")
            return

        # Parse metadata
        def parse_meta(m):
            try: return json.loads(m) if isinstance(m, str) else m
            except: return {}

        df['meta'] = df['metadata_json'].apply(parse_meta)
        df['raw_prob'] = df['meta'].apply(lambda x: x.get('raw_probability_up', 0.5))
        df['calib_prob'] = df['meta'].apply(lambda x: x.get('calibrated_probability_up', 0.5))

        print("\n--- Stored Probability Statistics ---")
        stats = {
            "Total Samples": len(df),
            "Unique Raw Probs": df['raw_prob'].nunique(),
            "Unique Calib Probs": df['calib_prob'].nunique(),
            "Raw Prob Mean": df['raw_prob'].mean(),
            "Calib Prob Mean": df['calib_prob'].mean(),
            "Raw Prob Std": df['raw_prob'].std(),
            "Calib Prob Std": df['calib_prob'].std(),
            "Raw Prob Min": df['raw_prob'].min(),
            "Raw Prob Max": df['raw_prob'].max(),
            "Identical Pairs (Raw == Calib)": (df['raw_prob'] == df['calib_prob']).sum()
        }
        for k, v in stats.items():
            print(f"{k}: {v}")

        if stats["Unique Raw Probs"] <= 1:
            print("\n[!] ALERT: Raw probabilities are CONSTANT. Model may be defaulting or broken.")

        if stats["Identical Pairs (Raw == Calib)"] == len(df):
            print("\n[!] ALERT: Raw and Calibrated probabilities are IDENTICAL. Calibration may be bypassed.")

        print("\n--- Sample Trace ---")
        print(df[['symbol', 'date', 'prediction', 'raw_prob', 'calib_prob']].head(20).to_markdown(index=False))

if __name__ == "__main__":
    forensic_audit()
