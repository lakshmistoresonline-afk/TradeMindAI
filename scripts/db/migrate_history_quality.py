import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def migrate():
    print(f"Connecting to: {db_url.split('@')[-1]}")
    with engine.connect() as conn:
        print("[*] Migrating quality_class for historical signals...")

        # 1. SWING -> PRIMARY
        res1 = conn.execute(text("UPDATE shadow_signals SET quality_class = 'PRIMARY' WHERE signal_type = 'SWING' AND quality_class IS NULL"))
        print(f"   Updated {res1.rowcount} SWING signals to PRIMARY.")

        # 2. SHORT -> EXPERIMENTAL (if any exist)
        res2 = conn.execute(text("UPDATE shadow_signals SET quality_class = 'EXPERIMENTAL' WHERE signal_type = 'SHORT' AND quality_class IS NULL"))
        print(f"   Updated {res2.rowcount} SHORT signals to EXPERIMENTAL.")

        # 3. Handle NULL signal_type (default to EXPERIMENTAL)
        res3 = conn.execute(text("UPDATE shadow_signals SET quality_class = 'EXPERIMENTAL' WHERE signal_type IS NULL AND quality_class IS NULL"))
        print(f"   Updated {res3.rowcount} UNKNOWN signals to EXPERIMENTAL.")

        conn.commit()
        print("[+] Migration successful.")

if __name__ == "__main__":
    migrate()
