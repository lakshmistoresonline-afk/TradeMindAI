import sqlite3
import json

conn = sqlite3.connect('backend/local_operational.db')
cursor = conn.cursor()
cursor.execute('SELECT symbol, horizon, roc_auc, hyperparameters FROM model_registry LIMIT 10')
rows = cursor.fetchall()
for row in rows:
    hp = json.loads(row[3]) if row[3] else {}
    print(f"{row[0]} ({row[1]}): AUC={row[2]}, test_size={hp.get('test_size')}, positives={hp.get('positives_test')}")
conn.close()
