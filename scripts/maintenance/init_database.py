import sys
import os

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core.postgres import init_db

if __name__ == "__main__":
    print("Initializing Database Schema...")
    init_db()
    print("Database Schema Initialized.")
