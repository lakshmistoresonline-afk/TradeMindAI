import json
import yaml
import sqlite3
import pandas as pd
from pathlib import Path

# Mock the engine to see if events are skipped
class MockEngine:
    def __init__(self, trades_path, db_path):
        with open(trades_path, 'r') as f:
            self.trades_data = json.load(f)['results']

        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT symbol, date FROM historical_prices", conn)
        conn.close()
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%dT%H:%M:%S')

        self.trading_dates = sorted(df['date'].unique())
        self.symbol_dates = {}
        for symbol, group in df.groupby('symbol'):
            self.symbol_dates[symbol] = sorted(group['date'].unique())

    def resolve_date(self, symbol, start_date, bars_offset):
        if symbol not in self.symbol_dates: return None
        dates = self.symbol_dates[symbol]
        try:
            # Find index of start_date or first date after it
            start_idx = -1
            for i, d in enumerate(dates):
                if d >= start_date:
                    start_idx = i
                    break
            if start_idx == -1: return None
            target_idx = start_idx + bars_offset
            if target_idx < len(dates): return dates[target_idx]
        except Exception: pass
        return None

def check():
    engine = MockEngine("docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json", "backend/local_operational.db")

    events = []
    for i, trade in enumerate(engine.trades_data):
        entry_date = engine.resolve_date(trade['symbol'], trade['signal_date'], trade['bars_to_entry'])
        if not entry_date: continue
        exit_date = engine.resolve_date(trade['symbol'], entry_date, trade['bars_in_position'])
        if not exit_date: continue
        events.append({'trade_id': i, 'type': 'ENTRY', 'date': entry_date})
        events.append({'trade_id': i, 'type': 'EXIT', 'date': exit_date})

    events.sort(key=lambda x: (x['date'], 0 if x['type'] == 'EXIT' else 1))

    event_idx = 0
    num_events = len(events)

    skipped_dates = set()
    for current_date in engine.trading_dates:
        while event_idx < num_events and events[event_idx]['date'] == current_date:
            event_idx += 1

    print(f"Total Events: {num_events}")
    print(f"Processed Events: {event_idx}")
    print(f"Remaining Events: {num_events - event_idx}")

    if event_idx < num_events:
        print(f"Next remaining event date: {events[event_idx]['date']}")
        print(f"Last trading date: {engine.trading_dates[-1]}")

if __name__ == "__main__":
    check()
