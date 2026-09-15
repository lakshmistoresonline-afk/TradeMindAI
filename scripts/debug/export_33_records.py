import requests
import json

def export():
    url = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"
    resp = requests.get(url)
    signals = resp.json()

    print("| Signal ID | Symbol | Dir | Horizon | Quality | Entry | Target | Stop | Prob | EV | R:R | Status | Created |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for s in signals:
        sid = s.get('id', 'UNAVAILABLE')
        sym = s.get('symbol', 'UNAVAILABLE')
        dir = s.get('direction', 'UNAVAILABLE')
        hor = s.get('timeframe', 'UNAVAILABLE')
        qual = s.get('quality_class') or ('PRIMARY' if hor == 'SWING' else 'EXPERIMENTAL')
        entry = s.get('entry_price', 0.0)
        target = s.get('target_price', 0.0)
        stop = s.get('stop_price', 0.0)
        curr = s.get('current_price', 0.0)
        prob = s.get('calibrated_probability', 0.0)
        ev = s.get('expected_value', 0.0)
        rr = s.get('risk_reward_ratio', 0.0)
        status = s.get('status', 'UNAVAILABLE')
        created = s.get('created_at', 'UNAVAILABLE')

        print(f"| {sid} | {sym} | {dir} | {hor} | {qual} | ₹{entry:,.1f} | ₹{target:,.1f} | ₹{stop:,.1f} | {prob:.1%} | {ev:+.2f} | 1:{rr:.1f} | {status} | {created} |")

if __name__ == "__main__":
    export()
