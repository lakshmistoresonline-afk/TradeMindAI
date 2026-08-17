import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import init_db

if __name__ == "__main__":
    print("[*] Initializing Database Schema...")
    init_db()
    print("[SUCCESS] Schema ready.")
