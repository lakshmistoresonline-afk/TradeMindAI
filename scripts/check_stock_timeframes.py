import os
import sys
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join("backend", ".env"))

db_url = os.getenv("POSTGRES_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

def check_stocks():
    if not db_url: return
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            print("--- STOCKS TABLE TIMEFRAME DISTRIBUTION ---")
            res = conn.execute(text("SELECT structured_consensus FROM stocks")).fetchall()

            tf_counts = {}
            rating_counts = {}
            tf_rating_counts = {}
            for row in res:
                if row[0]:
                    try:
                        data = json.loads(row[0])
                        tf = data.get('timeframe', 'MISSING')
                        tf_counts[tf] = tf_counts.get(tf, 0) + 1

                        rating = data.get('rating', 'MISSING')
                        rating_counts[rating] = rating_counts.get(rating, 0) + 1

                        key = f"{tf} | {rating}"
                        tf_rating_counts[key] = tf_rating_counts.get(key, 0) + 1
                    except:
                        tf_counts['ERROR'] = tf_counts.get('ERROR', 0) + 1
                else:
                    tf_counts['NONE'] = tf_counts.get('NONE', 0) + 1

            print("Timeframes:")
            for tf, count in tf_counts.items():
                print(f"  - {tf}: {count}")

            print("\nRatings:")
            for r, count in rating_counts.items():
                print(f"  - {r}: {count}")

            print("\nTimeframe | Rating Breakdown:")
            for tr, count in tf_rating_counts.items():
                print(f"  - {tr}: {count}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stocks()
