import sqlalchemy
from sqlalchemy import text
import os

url = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = sqlalchemy.create_engine(url)

def check():
    with engine.connect() as conn:
        live = conn.execute(text("SELECT count(*) FROM live_signals")).scalar()
        shadow = conn.execute(text("SELECT count(*) FROM shadow_signals")).scalar()
        print(f"Neon Status -> Live: {live}, Shadow: {shadow}")

if __name__ == "__main__":
    check()
