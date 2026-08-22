from sqlalchemy import create_engine, text
import os

POSTGRES_URL = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(POSTGRES_URL)

with engine.connect() as conn:
    regimes = conn.execute(text("SELECT COUNT(*) FROM market_regimes")).fetchone()[0]
    stocks = conn.execute(text("SELECT COUNT(*) FROM stocks")).fetchone()[0]
    prices = conn.execute(text("SELECT COUNT(*) FROM historical_prices")).fetchone()[0]
    signals = conn.execute(text("SELECT COUNT(*) FROM live_signals")).fetchone()[0]
    instruments = conn.execute(text("SELECT COUNT(*) FROM instruments")).fetchone()[0]

    print(f"Neon Regime Count: {regimes}")
    print(f"Neon Stock Count: {stocks}")
    print(f"Neon Price Count: {prices}")
    print(f"Neon Signal Count: {signals}")
    print(f"Neon Instrument Count: {instruments}")

engine.dispose()
