import datetime
from fastapi.encoders import jsonable_encoder
import json

dt = datetime.datetime(2026, 8, 15, 10, 0, 0)
encoded = jsonable_encoder(dt)
print(f"Naive: {encoded}")

dt_utc = datetime.datetime(2026, 8, 15, 10, 0, 0, tzinfo=datetime.timezone.utc)
encoded_utc = jsonable_encoder(dt_utc)
print(f"Aware UTC: {encoded_utc}")
