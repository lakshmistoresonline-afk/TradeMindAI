
import os
import json
import pandas as pd
import numpy as np

def audit():
    csv_path = "validation/shadow/shadow_observations.csv"
    if not os.path.exists(csv_path):
        print("Observations CSV not found")
        return

    df = pd.read_csv(csv_path)

    # 1. Probability Distribution
    # Filter only those that reached inference (status not model/data error)
    inf_df = df[df['calibrated_prob'].notna()]

    if inf_df.empty:
        print("No inference data available for drift audit.")
        return

    stats = {
        "prob_mean": float(inf_df['calibrated_prob'].mean()),
        "prob_std": float(inf_df['calibrated_prob'].std()),
        "prob_min": float(inf_df['calibrated_prob'].min()),
        "prob_max": float(inf_df['calibrated_prob'].max()),
        "prob_median": float(inf_df['calibrated_prob'].median()),

        "raw_prob_mean": float(inf_df['raw_prob'].mean()),
        "raw_prob_median": float(inf_df['raw_prob'].median()),

        "evaluations_count": len(inf_df)
    }

    print("Probability Audit:")
    print(json.dumps(stats, indent=4))

    # 2. Rejection Analysis
    rejections = df['rejection_reason'].value_counts().to_dict()
    print("\nRejection Breakdown:")
    print(json.dumps(rejections, indent=4))

    # Save to JSON
    with open("validation/results/drift_analysis.json", "w") as f:
        json.dump(stats, f, indent=4)

if __name__ == "__main__":
    audit()
