import sys
import os
from pydantic import ValidationError

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.config import Settings

def test_config():
    print("CLAIM: Production startup fails on insecure configuration")
    print("-" * 60)

    try:
        # Simulate production environment with default secret
        s = Settings(ENVIRONMENT="production", SECRET_KEY="SECRET")
        print("RESULT: FAIL (Startup allowed with default SECRET)")
    except ValidationError as e:
        print(f"PASS: Caught expected validation error: {e.errors()[0]['msg']}")

    try:
        # Simulate production environment with weak secret
        s = Settings(ENVIRONMENT="production", SECRET_KEY="too-short")
        print("RESULT: FAIL (Startup allowed with weak SECRET)")
    except ValidationError as e:
        print(f"PASS: Caught expected validation error: {e.errors()[0]['msg']}")

    try:
        # Simulate production environment with default ingest key
        s = Settings(ENVIRONMENT="production", SECRET_KEY="A"*32, MARKET_DATA_INGEST_KEY="LOCAL_ONLY_DEV_KEY")
        print("RESULT: FAIL (Startup allowed with default INGEST_KEY)")
    except ValidationError as e:
        print(f"PASS: Caught expected validation error: {e.errors()[0]['msg']}")

if __name__ == "__main__":
    test_config()
