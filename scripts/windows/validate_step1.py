import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def validate():
    db_url = os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not set.")
        sys.exit(1)

    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            # 1. Check Stocks Count
            count = conn.execute(text('SELECT count(*) FROM stocks')).scalar()
            print(f"STOCKS_COUNT: {count}")

            # 2. Check F&O Instruments
            fo_count = conn.execute(text("SELECT count(*) FROM instruments WHERE segment IN ('FUTURES', 'OPTIONS')")).scalar()
            print(f"FO_COUNT: {fo_count}")

            # 3. Check for Null Metadata in Options
            null_meta = conn.execute(text("SELECT count(*) FROM live_signals WHERE asset_class = 'OPTIONS' AND (strike IS NULL OR option_type IS NULL)")).scalar()
            print(f"NULL_METADATA: {null_meta}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate()
