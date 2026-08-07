import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from sqlalchemy.orm import Session
import asyncio
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import db_client
from backend.core.postgres import SessionLocal, init_db, StockDB, PriceDB, RegimeDB
from backend.domain.models.stock import Stock

async def migrate():
    print("--- STARTING MIGRATION: FIRESTORE -> HYBRID ARCHITECTURE ---")
    init_db()
    pg = SessionLocal()
    fs = db_client

    # 1. Migrate Stocks
    print("Migrating Stocks...")
    stocks_ref = fs.collection("stocks").stream()
    for doc in stocks_ref:
        data = doc.to_dict()
        # Clean data for SQL
        db_stock = StockDB(
            symbol=data['symbol'],
            name=data.get('name'),
            sector=data.get('sector'),
            industry=data.get('industry'),
            last_price=data.get('last_price'),
            change_pct=data.get('change_pct'),
            market_cap=data.get('market_cap'),
            pe_ratio=data.get('pe_ratio'),
            pb_ratio=data.get('pb_ratio'),
            analysis=data.get('analysis'),
            health_metrics=data.get('health_metrics'),
            confidence_metrics=data.get('confidence_metrics')
        )
        pg.merge(db_stock)

        # 2. Migrate Prices (Sub-collection)
        print(f"  -> Migrating Prices for {data['symbol']}...")
        prices_ref = fs.collection("stocks").document(data['symbol']).collection("prices").stream()
        for p_doc in prices_ref:
            p_data = p_doc.to_dict()
            db_price = PriceDB(
                symbol=data['symbol'],
                date=p_data['date'],
                open=p_data['open'],
                high=p_data['high'],
                low=p_data['low'],
                close=p_data['close'],
                volume=p_data['volume'],
                indicators=p_data.get('indicators')
            )
            pg.add(db_price)

    # 3. Migrate Market Regimes
    print("Migrating Market Regimes...")
    regimes_ref = fs.collection("market_regimes").stream()
    for doc in regimes_ref:
        data = doc.to_dict()
        db_regime = RegimeDB(
            date=data['date'],
            regime=data['regime'],
            risk_mode=data['risk_mode'],
            description=data['description'],
            volatility_index=data['volatility_index']
        )
        pg.add(db_regime)

    pg.commit()
    pg.close()
    print("--- MIGRATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(migrate())
