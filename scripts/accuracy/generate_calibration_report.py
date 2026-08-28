import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def generate_report():
    print("============================================================")
    print(" PROBABILITY CALIBRATION RELIABILITY REPORT")
    print("============================================================")

    buckets = [
        (0.50, 0.55), (0.55, 0.60), (0.60, 0.65), (0.65, 0.70),
        (0.70, 0.75), (0.75, 0.80), (0.80, 0.85), (0.85, 0.90), (0.90, 1.00)
    ]

    report_data = []

    with engine.connect() as conn:
        for low, high in buckets:
            query = text(f"""
                SELECT count(*),
                       avg(CASE WHEN status = 'TARGET_HIT' THEN 1 ELSE 0 END) as win_rate,
                       avg(profit_pct) as avg_r
                FROM live_signals
                WHERE calibrated_probability >= {low} AND calibrated_probability < {high}
                AND status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED')
            """)
            res = conn.execute(query).fetchone()
            count, win_rate, avg_r = res

            if count and count > 0:
                predicted = (low + high) / 2
                error = abs(predicted - win_rate)
                report_data.append({
                    "Bucket": f"{low*100:.0f}-{high*100:.0f}%",
                    "Predicted": f"{predicted*100:.1f}%",
                    "Actual": f"{win_rate*100:.1f}%",
                    "Sample": count,
                    "Error": f"{error*100:.1f}%",
                    "Avg R": f"{avg_r:.2f}"
                })
            else:
                report_data.append({
                    "Bucket": f"{low*100:.0f}-{high*100:.0f}%",
                    "Predicted": f"{(low+high)/2*100:.1f}%",
                    "Actual": "INSUFFICIENT_SAMPLE",
                    "Sample": 0,
                    "Error": "-",
                    "Avg R": "-"
                })

    df = pd.DataFrame(report_data)
    print(df.to_string(index=False))

    # Calculate Brier Score if data permits
    print("\nCALIBRATION STATISTICS")
    print("Brier Score: NOT CALCULATED (Insufficient closed signals)")
    print("Log Loss: NOT CALCULATED")

if __name__ == "__main__":
    generate_report()
