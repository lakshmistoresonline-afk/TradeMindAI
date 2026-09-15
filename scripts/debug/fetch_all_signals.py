import requests
import json

def fetch():
    url = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"
    resp = requests.get(url)
    signals = resp.json()

    print(f"| Signal ID | Symbol | Direction | Horizon | Quality (API) | Entry | Target | Stop | Current | Prob | EV | R:R | Status | Created |")
    print(f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for s in signals:
        sid = s.get('id', 'N/A')
        sym = s.get('symbol', 'N/A')
        dir = s.get('direction', 'N/A')
        hor = s.get('timeframe', 'N/A')
        qual = s.get('quality_class', 'UNAVAILABLE')
        entry = s.get('entry_price', 0.0)
        target = s.get('target_price', 0.0)
        stop = s.get('stop_price', 0.0)
        curr = s.get('current_price', 0.0)
        prob = s.get('calibrated_probability', 0.0)
        ev = s.get('expected_value', 0.0)
        rr = s.get('risk_reward_ratio', 0.0)
        status = s.get('status', 'N/A')
        created = s.get('created_at', 'N/A')

        print(f"| {sid} | {sym} | {dir} | {hor} | {qual} | ₹{entry:,.1f} | ₹{target:,.1f} | ₹{stop:,.1f} | ₹{curr:,.1f} | {prob:.1%} | {ev:+.2f} | 1:{rr:.1f} | {status} | {created} |")

if __name__ == "__main__":
    fetch()
