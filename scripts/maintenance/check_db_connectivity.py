import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

load_dotenv('backend/.env')

def check_connectivity():
    db_url = os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        # Fallback to local sqlite for dev if not specified
        db_url = "sqlite:///./backend/local_operational.db"
        print(f"INFO: No DATABASE_URL found. Using fallback: {db_url}")

    print(f"DEBUG: Testing connection to: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[+] Database connectivity: SUCCESS")
        return True
    except Exception as e:
        print(f"[!] Database connectivity: FAIL - {e}")
        return False

if __name__ == "__main__":
    if check_connectivity():
        sys.exit(0)
    else:
        sys.exit(1)
