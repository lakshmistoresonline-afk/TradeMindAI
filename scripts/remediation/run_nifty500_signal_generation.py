"""
================================================================================
TradeMindAI: Master Nifty 500 Signal Generation & Ledger Population Script
================================================================================
Executes EquitySignalGenerationService.run_production_scan() across all 500
active Nifty equities using authentic market price data in PriceDB.
Persists eligible signals into LiveSignalDB and ShadowSignalDB ledgers.
================================================================================
"""

import os
import sys
import asyncio
import logging
import json

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.services.equity_signal_generation_service import EquitySignalGenerationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def generate_nifty500_signals():
    logger.info("=== Starting Nifty 500 Master Signal Generation Scan ===")
    results = await EquitySignalGenerationService.run_production_scan()

    logger.info("=== Signal Generation Scan Summary ===")
    logger.info(f"  Scan ID             : {results.get('scan_id')}")
    logger.info(f"  Source Symbol Count : {results.get('source_symbol_count')}")
    logger.info(f"  Symbols Attempted   : {results.get('symbols_attempted')}")
    logger.info(f"  Candidate BUY Count : {results.get('candidate_buy_count')}")
    logger.info(f"  Signals Persisted   : {results.get('signals_persisted')}")
    logger.info(f"  Scan Status         : {results.get('status')}")
    logger.info(f"  Scan Duration (s)   : {results.get('duration_seconds'):.2f}")

if __name__ == "__main__":
    asyncio.run(generate_nifty500_signals())
