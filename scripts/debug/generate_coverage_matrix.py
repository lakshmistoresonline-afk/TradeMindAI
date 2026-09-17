import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def generate():
    with engine.connect() as conn:
        print("[*] Generating Model Coverage Matrix...")

        sql = """
        SELECT symbol,
               COUNT(*) as prediction_count,
               MIN(timestamp) as earliest_prediction,
               MAX(timestamp) as latest_prediction
        FROM predictions
        GROUP BY symbol
        ORDER BY prediction_count DESC
        """
        df = pd.read_sql(sql, conn)

        # Calculate coverage % against hypothetical daily scan for 2 years (~500 days)
        df['coverage_pct'] = (df['prediction_count'] / 500 * 100).clip(upper=100).round(1)

        # Save to CSV for auditable evidence
        df.to_csv('reports/MODEL_COVERAGE_MATRIX_V22.csv', index=False)
        print(f"[+] Coverage matrix saved to reports/MODEL_COVERAGE_MATRIX_V22.csv")

        # Top 10 Summary for Markdown
        print("\nTop 10 Coverage Symbols:")
        print(df.head(10).to_string())

if __name__ == "__main__":
    generate()
