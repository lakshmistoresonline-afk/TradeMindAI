"""
================================================================================
TradeMindAI: Fast Complete Backfill & AZAD Alias Reconciler (Fail-Closed Secure)
================================================================================
Synthetic OHLCV generation is strictly prohibited. Missing data remains missing.
================================================================================
"""

import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB, StockDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS, validate_nifty500_universe

def fast_complete_all_500():
    print("================================================================================")
    print("  TRADEMIND AI: FAIL-CLOSED SECURE UNIVERSE READINESS ENGINE")
    print("================================================================================\n")
    print("[SECURITY POLICY] Synthetic OHLCV generation is permanently disabled.")
    print("[SECURITY POLICY] Row deletion during backfill is permanently disabled.")
    raise ValueError("CRITICAL SECURITY VIOLATION: Synthetic price generation and unauthorized row deletion are strictly prohibited by fail-closed safety policy.")

if __name__ == "__main__":
    try:
        fast_complete_all_500()
    except Exception as e:
        print(f"[BLOCKED SUCCESSFULLY] {e}")
        sys.exit(1)
