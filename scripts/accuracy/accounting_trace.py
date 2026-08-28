import json
import yaml
import sqlite3
import pandas as pd
from datetime import datetime

class TracingEngine:
    def __init__(self):
        with open('config/portfolio_backtest.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
            self.trades_data = json.load(f)['results']
        conn = sqlite3.connect('backend/local_operational.db')
        df = pd.read_sql_query("SELECT symbol, date, close FROM historical_prices", conn)
        conn.close()
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        self.price_data = {}
        for row in df.itertuples():
            if row.date not in self.price_data: self.price_data[row.date] = {}
            self.price_data[row.date][row.symbol] = row.close
        self.trading_dates = sorted(self.price_data.keys())
        self.symbol_dates = {}
        for symbol, group in df.groupby('symbol'):
            self.symbol_dates[symbol] = sorted(group['date'].unique())

    def resolve_date(self, symbol, start_date, bars_offset):
        dates = self.symbol_dates.get(symbol, [])
        try:
            start_idx = -1
            for i, d in enumerate(dates):
                if d >= start_date:
                    start_idx = i
                    break
            if start_idx == -1: return None
            target_idx = start_idx + bars_offset
            if target_idx < len(dates): return dates[target_idx]
        except: pass
        return None

    def calculate_costs(self, price, quantity, is_buy):
        c = self.config['costs']
        value = price * quantity
        brokerage = value * c['brokerage_per_leg']
        exchange = value * c['exchange_charges']
        gst = (brokerage + exchange) * c['gst_on_brokerage_plus_exchange']
        sebi = value * c['sebi_charges']
        stt = value * (c['stt_delivery_buy'] if is_buy else c['stt_delivery_sell'])
        stamp = value * (c['stamp_duty'] if is_buy else 0)
        return brokerage + exchange + gst + sebi + stt + stamp

    def trace(self, target_date_str):
        target_date = datetime.strptime(target_date_str, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        cash = 1000000.0
        positions = {}

        events = []
        for i, t in enumerate(self.trades_data):
            en_date = self.resolve_date(t['symbol'], t['signal_date'], t['bars_to_entry'])
            if not en_date: continue
            ex_date = self.resolve_date(t['symbol'], en_date, t['bars_in_position'])
            if not ex_date: continue
            events.append({'tid': i, 'type': 'ENTRY', 'date': en_date, 't': t})
            events.append({'tid': i, 'type': 'EXIT', 'date': ex_date, 't': t})
        events.sort(key=lambda x: (x['date'], 0 if x['type'] == 'EXIT' else 1))

        ev_idx = 0
        total_pnl_ledger = 0.0

        for d in self.trading_dates:
            # EXITS
            while ev_idx < len(events) and events[ev_idx]['date'] == d and events[ev_idx]['type'] == 'EXIT':
                ev = events[ev_idx]
                if ev['tid'] in positions:
                    pos = positions.pop(ev['tid'])
                    # Slipped prices (using 0 slippage for forensic)
                    ex_price = float(ev['t']['exit'])
                    ex_costs = self.calculate_costs(ex_price, pos['qty'], is_buy=(pos['dir'] == 'SHORT'))

                    if pos['dir'] == 'LONG':
                        pnl = (ex_price - pos['price']) * pos['qty'] - (pos['e_costs'] + ex_costs)
                        cash += (ex_price * pos['qty']) - ex_costs
                    else:
                        pnl = (pos['price'] - ex_price) * pos['qty'] - (pos['e_costs'] + ex_costs)
                        cash += (2 * pos['price'] * pos['qty'] - ex_price * pos['qty'] - ex_costs)

                    total_pnl_ledger += pnl
                ev_idx += 1

            # EQUITY (before entries)
            val_locked = sum(p['price'] * p['qty'] for p in positions.values())
            unrealized = 0
            for p in positions.values():
                mark = self.price_data[d].get(p['symbol'], p['price'])
                unrealized += (mark - p['price']) * p['qty'] if p['dir'] == 'LONG' else (p['price'] - mark) * p['qty']
            equity = cash + val_locked + unrealized

            # ENTRIES
            while ev_idx < len(events) and events[ev_idx]['date'] == d and events[ev_idx]['type'] == 'ENTRY':
                ev = events[ev_idx]
                if len(positions) < 10:
                    t = ev['t']
                    price_risk = abs(float(t['actual_entry']) - float(t['stop']))
                    if price_risk > 1e-6:
                        qty = int((equity * 0.01) / price_risk)
                        # Cap
                        if float(t['actual_entry']) * qty > equity * 0.1:
                            qty = int((equity * 0.1) / float(t['actual_entry']))

                        if qty > 0:
                            e_price = float(t['actual_entry'])
                            e_costs = self.calculate_costs(e_price, qty, is_buy=(t['direction'] == 'LONG'))
                            if cash >= (e_price * qty + e_costs):
                                cash -= (e_price * qty + e_costs)
                                positions[ev['tid']] = {'dir': t['direction'], 'price': e_price, 'qty': qty, 'e_costs': e_costs, 'symbol': t['symbol']}
                ev_idx += 1

            if d == target_date:
                print(f"--- TRACE FOR {d} ---")
                print(f"Cash: {cash:,.2f}")
                print(f"Equity: {equity:,.2f}")
                print(f"Ledger PnL: {total_pnl_ledger:,.2f}")
                print(f"Expected Equity (Start + PnL): {1000000.0 + total_pnl_ledger:,.2f}")
                print(f"Discrepancy: {equity - (1000000.0 + total_pnl_ledger):,.2f}")
                break

if __name__ == "__main__":
    t = TracingEngine()
    t.trace('2020-03-23T00:00:00')
