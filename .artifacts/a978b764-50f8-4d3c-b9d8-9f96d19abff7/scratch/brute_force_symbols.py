from yahooquery import Ticker
import pandas as pd

def check(symbol):
    t = Ticker(symbol)
    p = t.price
    if isinstance(p, dict) and symbol in p and isinstance(p[symbol], dict):
        return p[symbol].get('shortName') or p[symbol].get('longName') or "FOUND"
    return None

variants = [
    "LTIM.NS", "LTIMIND.NS", "LTIMINDTREE.NS", "LTI.NS", "MINDTREE.NS",
    "PEL.NS", "PIRAMAL.NS", "PIRAMALENT.NS", "PIRAMALFIN.NS",
    "ZOMATO.NS", "ETERNAL.NS"
]

print("--- Symbol Brute Force ---")
for v in variants:
    name = check(v)
    if name:
        print(f"{v}: {name}")
    else:
        print(f"{v}: NOT FOUND")
