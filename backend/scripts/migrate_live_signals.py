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

    from backend.core.postgres import LiveSignalDB
    engine = create_engine(DATABASE_URL)

    # Reflect existing table
    from sqlalchemy import inspect
    inspector = inspect(engine)
    existing_cols = {c["name"] for c in inspector.get_columns("live_signals")}

    # Get defined columns in SQLAlchemy model
    defined_cols = LiveSignalDB.__table__.columns

    with engine.connect() as conn:
        for col in defined_cols:
            if col.name not in existing_cols:
                col_type = str(col.type).split('(')[0] # Simplified type
                # Map specific types if necessary
                if "VARCHAR" in col_type: col_type = "VARCHAR"
                if "FLOAT" in col_type: col_type = "FLOAT"
                if "DATETIME" in col_type: col_type = "TIMESTAMP"
                if "BOOLEAN" in col_type: col_type = "BOOLEAN"
                if "INTEGER" in col_type: col_type = "INTEGER"

                try:
                    conn.execute(text(f"ALTER TABLE live_signals ADD COLUMN {col.name} {col_type};"))
                    conn.commit()
                    print(f"Added missing column: {col.name} ({col_type})")
                except Exception as e:
                    conn.rollback()
                    print(f"Error adding {col.name}: {e}")

        # Also ensure UNIQUE constraint exists
        try:
            conn.execute(text("ALTER TABLE live_signals ADD CONSTRAINT _symbol_strategy_direction_ts_uc UNIQUE (symbol, strategy_version, direction, decision_timestamp);"))
            conn.commit()
            print("Added unique constraint.")
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e):
                print("Unique constraint already exists.")
            else:
                print(f"Error adding unique constraint: {e}")

if __name__ == "__main__":
    main()
