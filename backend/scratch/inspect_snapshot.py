import json
import pandas as pd

def inspect():
    with open('backend/data/forensics/ledger_snapshot.json', 'r') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    print(f"Total Signals: {len(df)}")
    print("\nEvaluation Modes:")
    print(df['evaluation_mode'].value_counts())
    print("\nStatuses:")
    print(df['status'].value_counts())
    print("\nStrategy Versions:")
    print(df['strategy_version'].value_counts())

    # Filter for V2.2 population
    v22 = df[df['strategy_version'] == 'v2.2']
    print(f"\nV2.2 Signals: {len(v22)}")
    print(v22['status'].value_counts())

    # Check for STOP_LOSS
    sl = v22[v22['status'] == 'STOP_LOSS']
    print(f"\nV2.2 STOP_LOSS Signals: {len(sl)}")
    if not sl.empty:
        print(sl[['symbol', 'timestamp', 'entry_price', 'stop_price', 'target_price']].head())

if __name__ == "__main__":
    inspect()
