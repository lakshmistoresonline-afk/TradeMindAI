import sys
from curl_cffi import requests as curleq

# Monkey-patch requests
import requests
original_session = requests.Session

class PatchedSession(curleq.Session):
    def __init__(self, *args, **kwargs):
        # Force impersonate chrome for all sessions
        if 'impersonate' not in kwargs:
            kwargs['impersonate'] = 'chrome'
        super().__init__(*args, **kwargs)

    # yfinance uses some requests-specific attributes that might be missing in curl_cffi
    # but curl_cffi.Session is mostly compatible.
    @property
    def cookies(self):
        return super().cookies

requests.Session = PatchedSession
# Also patch top-level functions just in case
requests.get = curleq.get
requests.post = curleq.post

import yfinance as yf
print("[*] Testing patched yfinance...")
try:
    msft = yf.Ticker('MSFT')
    hist = msft.history(period='5d')
    print(hist.head())
    if not hist.empty:
        print("[SUCCESS] Patched yfinance worked!")
    else:
        print("[FAIL] History is empty.")
except Exception as e:
    print(f"[ERROR] {e}")
