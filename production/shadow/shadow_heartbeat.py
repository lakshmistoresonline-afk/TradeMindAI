
import os
import sys
import json
from datetime import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal

class ShadowHeartbeat:
    @staticmethod
    def record_heartbeat(component: str, status: str = "ONLINE"):
        """
        Records a heartbeat for a specific shadow component (worker or scheduler).
        """
        try:
            with SessionLocal() as session:
                # We'll use a simple KV pattern or shadow_events for now,
                # but let's assume a dedicated system table or ShadowEventDB for health.
                from backend.core.postgres import ShadowEventDB

                payload = {"component": component, "status": status, "version": "v2.2"}
                event = ShadowEventDB(
                    event_type="HEARTBEAT",
                    symbol="SYSTEM",
                    timestamp=datetime.utcnow(),
                    decision=status,
                    payload_json=json.dumps(payload)
                )
                session.add(event)
                session.commit()
                # print(f"   [HEARTBEAT] {component} is {status}")
        except Exception as e:
            print(f"[!] Heartbeat Error: {e}")

if __name__ == "__main__":
    comp = sys.argv[1] if len(sys.argv) > 1 else "TEST"
    ShadowHeartbeat.record_heartbeat(comp)
