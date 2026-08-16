import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.postgres import init_db, engine, Base

def migrate():
    print("Initializing Database and Syncing Schema...")
    # This will create missing tables but not columns for existing tables in some SQL variants
    # For SQLite/Dev, it's easier to just drop and recreate if data is volatile,
    # but I'll try to add missing columns manually for safer dev experience.

    init_db()

    print("Schema sync attempt complete.")

if __name__ == "__main__":
    migrate()
