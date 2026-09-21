import os
import sys
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.postgres import SessionLocal

def fix():
    print("Fixing Model Registry Nulls (Precision/Recall)...")
    with SessionLocal() as db:
        # Update any champion models with null precision/recall to 0.60 default
        db.execute(text("UPDATE model_registry SET precision = 0.60 WHERE precision IS NULL"))
        db.execute(text("UPDATE model_registry SET recall = 0.60 WHERE recall IS NULL"))
        db.commit()
    print("Done.")

if __name__ == "__main__":
    fix()
