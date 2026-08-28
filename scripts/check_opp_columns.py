import os
import sys
from sqlalchemy import inspect
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def check():
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("opportunities")]
    print(f"Opportunities columns: {columns}")

if __name__ == "__main__":
    check()
