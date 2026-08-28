import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine, Base

def initialize():
    print(f"[*] Initializing database schema on: {engine.url}")
    try:
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database schema initialized/updated.")
    except Exception as e:
        print(f"[!] Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    initialize()
