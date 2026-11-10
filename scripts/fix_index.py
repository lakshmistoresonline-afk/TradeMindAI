import os

path = 'backend/core/postgres.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_str = "Index('idx_unique_active_signal', 'symbol', 'timeframe', unique=True"
new_str = "Index('idx_unique_active_signal', 'symbol', unique=True"

if old_str in text:
    text = text.replace(old_str, new_str)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("UPDATED_POSTGRES_INDEX_SUCCESSFULLY")
else:
    print("INDEX_ALREADY_UPDATED_OR_NOT_FOUND")
