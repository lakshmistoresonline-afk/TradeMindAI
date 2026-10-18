import os
import sys
import asyncio

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.services.signal_engine import SignalEngine
from backend.core.postgres import SessionLocal, StockDB

async def test_generation():
    with SessionLocal() as session:
        stocks = [s.symbol for s in session.query(StockDB).limit(5).all()]

    print('Testing signal generation on sample stocks after ML fallback update:', stocks)
    for sym in stocks:
        try:
            sig = await SignalEngine.generate_signal(symbol=sym, asset_class='EQUITY', timeframe='SWING')
            if sig:
                print(f'  - {sym}: SUCCESS -> {sig.symbol} | Dir: {sig.direction} | Entry: ₹{sig.entry_price}')
            else:
                print(f'  - {sym}: result = None')
        except Exception as e:
            print(f'  - {sym}: exception = {e}')

if __name__ == '__main__':
    asyncio.run(test_generation())
