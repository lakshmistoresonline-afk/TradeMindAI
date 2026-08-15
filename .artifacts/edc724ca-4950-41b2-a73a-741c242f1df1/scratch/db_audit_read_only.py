import os
import sys
import json
from sqlalchemy import text, create_engine, inspect
from dotenv import load_dotenv

# Add project root to path
sys.path.append("D:/TradeMindAI")
load_dotenv("D:/TradeMindAI/backend/.env")

def audit():
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    if not POSTGRES_URL:
        print("Error: POSTGRES_URL not found in .env")
        return

    engine = create_engine(POSTGRES_URL)
    inspector = inspect(engine)

    report = {
        "tables": []
    }

    with engine.connect() as conn:
        table_names = inspector.get_table_names()
        for table_name in table_names:
            table_info = {
                "name": table_name,
                "columns": [],
                "pk": inspector.get_pk_constraint(table_name)["constrained_columns"],
                "fk": inspector.get_foreign_keys(table_name),
                "indexes": inspector.get_indexes(table_name),
                "count": 0,
                "sample": []
            }

            # Get columns
            for column in inspector.get_columns(table_name):
                table_info["columns"].append({
                    "name": column["name"],
                    "type": str(column["type"])
                })

            # Get count
            try:
                count_res = conn.execute(text(f"SELECT count(*) FROM \"{table_name}\""))
                table_info["count"] = count_res.scalar()
            except Exception as e:
                table_info["count_error"] = str(e)

            # Get sample (if populated)
            if table_info["count"] > 0:
                try:
                    sample_res = conn.execute(text(f"SELECT * FROM \"{table_name}\" LIMIT 1"))
                    row = sample_res.fetchone()
                    if row:
                        # Convert row to dict for serializable report
                        table_info["sample"] = {k: str(v) if hasattr(v, 'isoformat') else v for k, v in row._asdict().items()}
                except Exception as e:
                    table_info["sample_error"] = str(e)

            report["tables"].append(table_info)

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    audit()
