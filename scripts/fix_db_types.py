import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def fix():
    with engine.connect() as conn:
        print("Fixing ai_status type...")
        conn.execute(text("ALTER TABLE stocks ALTER COLUMN ai_status TYPE VARCHAR(50) USING ai_status::text"))
        print("Fixing ai_last_error type...")
        conn.execute(text("ALTER TABLE stocks ALTER COLUMN ai_last_error TYPE TEXT USING ai_last_error::text"))

        print("Initializing PENDING status for all stocks...")
        conn.execute(text("UPDATE stocks SET ai_status = 'PENDING' WHERE ai_status IS NULL OR ai_status = ''"))

        conn.commit()
    print("Database types and initial values fixed.")

if __name__ == "__main__":
    fix()
