import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine, Base

def run_migration():
    print("--- TRADEMIND AI: PHASE 7C SCHEMA MIGRATION ---")

    # Use Base.metadata.create_all to create new tables
    Base.metadata.create_all(bind=engine)
    print("[*] Intelligence tables created.")

    with engine.connect() as conn:
        # Check for any column changes in existing tables if needed
        # (Already cleaned up ShadowSignalDB in postgres.py, might need to drop/recreate if it was messy)
        pass

    print("\n[SUCCESS] Phase 7C Migration Complete.")

if __name__ == "__main__":
    run_migration()
