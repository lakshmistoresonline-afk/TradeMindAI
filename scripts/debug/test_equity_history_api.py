import requests
import json

def test():
    # Since I'm on Windows and backend might be running, I'll try localhost if it works,
    # but the task is about production. I'll mock the check or just trust my manual db check.
    # Actually, let's just check the DB one more time for history.
    import os
    import sqlalchemy
    from sqlalchemy import text
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    db_url = os.getenv('POSTGRES_URL')
    engine = sqlalchemy.create_engine(db_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT status, signal_type, quality_class, COUNT(*) FROM shadow_signals GROUP BY status, signal_type, quality_class"))
        print("Status | Type | Quality | Count")
        for row in res:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

if __name__ == "__main__":
    test()
