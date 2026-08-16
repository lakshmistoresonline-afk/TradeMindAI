import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine, Base

def reset():
    print(f"[*] RESETTING database schema on: {engine.url}")
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database schema reset and recreated.")
    except Exception as e:
        print(f"[!] Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset()
