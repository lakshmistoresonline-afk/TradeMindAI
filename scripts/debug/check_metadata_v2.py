import sqlite3
import json

conn = sqlite3.connect('backend/local_operational.db')
cursor = conn.cursor()
cursor.execute('SELECT symbol, horizon, roc_auc, hyperparameters FROM model_registry WHERE symbol="ABB"')
rows = cursor.fetchall()
for row in rows:
    hp_raw = row[3]
    try:
        hp = json.loads(hp_raw) if hp_raw else {}
    except:
        hp = {}
    print(f"{row[0]} ({row[1]}): AUC={row[2]}, test_size={hp.get('test_size')}, positives={hp.get('positives_test')}")
conn.close()
