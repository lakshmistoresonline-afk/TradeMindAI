import json
import datetime

with open('web/public/signals.json', 'r') as f:
    signals = json.load(f)

print("Total signals in json:", len(signals))
raw_active = 0
for s in signals:
    # check date
    created_at = s.get('created_at')
    gen_time = datetime.datetime.fromisoformat(created_at).timestamp() * 1000
    horizon = s.get('timeframe', 'SWING').upper()
    max_age_hours = 720 if horizon == 'SWING' else (168 if horizon == 'SHORT' else 8760)
    age_hours = (datetime.datetime.now().timestamp() * 1000 - gen_time) / (1000 * 60 * 60)
    if age_hours <= max_age_hours:
        raw_active += 1

print(f"Active within age limit: {raw_active}")
