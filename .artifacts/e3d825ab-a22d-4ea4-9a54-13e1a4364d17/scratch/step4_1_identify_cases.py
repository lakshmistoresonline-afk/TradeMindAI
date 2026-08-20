import json
import pandas as pd

def identify():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    with open(results_path, 'r') as f:
        data = json.load(f)

    results = data['results']
    audit_data = []

    for t in results:
        actual_entry = t.get('actual_entry')
        stop = t.get('stop')
        direction = t.get('direction')

        if actual_entry is None or stop is None:
            continue

        gap_through_stop = False
        if direction == 'LONG':
            if actual_entry < stop:
                gap_through_stop = True
        else: # SHORT
            if actual_entry > stop:
                gap_through_stop = True

        if gap_through_stop:
            t['gap_through_stop'] = True
            audit_data.append(t)

    cols = ['symbol', 'signal_date', 'direction', 'intended_entry', 'actual_entry',
            'target', 'stop', 'exit', 'outcome', 'profit_pct',
            'bars_to_entry', 'bars_in_position', 'entry_execution_type', 'gap_through_stop']

    if not audit_data:
        print("No gap-through-stop cases identified.")
        pd.DataFrame(columns=cols).to_csv('docs/STEP4_GAP_THROUGH_STOP_AUDIT.csv', index=False)
        return

    df_audit = pd.DataFrame(audit_data)
    df_audit = df_audit[cols]
    df_audit.to_csv('docs/STEP4_GAP_THROUGH_STOP_AUDIT.csv', index=False)
    print(f"Identified {len(df_audit)} gap-through-stop cases.")

if __name__ == "__main__":
    identify()
