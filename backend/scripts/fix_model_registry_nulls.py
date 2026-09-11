import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DATABASE_URL = os.getenv("POSTGRES_URL")

def main():
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE model_registry
            SET hyperparameters='{}',
                feature_importances='{}',
                calibration_metadata='{}',
                last_trained=NOW()
            WHERE hyperparameters IS NULL;
        """))
        conn.commit()
        print("Updated NULL values in model_registry.")

if __name__ == "__main__":
    main()
