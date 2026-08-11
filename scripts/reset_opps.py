import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def reset():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM opportunities"))
        conn.commit()
        print("[*] Opportunities table cleared.")

if __name__ == "__main__":
    reset()
