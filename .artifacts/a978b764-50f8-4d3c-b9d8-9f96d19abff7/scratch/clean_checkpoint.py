import json
import os

CHECKPOINT_FILE = "backend/data/sync_checkpoint.json"
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, 'r') as f:
        data = json.load(f)

    # Remove failed ones to force retry
    to_remove = []
    for k, v in data.items():
        if v.get("status") != "SUCCESS":
            to_remove.append(k)

    for k in to_remove:
        del data[k]
        print(f"Removed {k} from checkpoint.")

    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(data, f, indent=4)
