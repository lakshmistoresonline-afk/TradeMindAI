from yahooquery import Ticker
import json

def test():
    print("[*] Testing NIFTY Derivatives with YahooQuery...")
    t = Ticker('^NSEI')

    print("\n[2] Option Chain Test:")
    try:
        oc = t.option_chain
        print(f"Type: {type(oc)}")
        if isinstance(oc, str):
            print(f"Content: {oc[:200]}")
        else:
            print(oc)
    except Exception as e:
        print(f"Option Chain Error: {e}")

if __name__ == "__main__":
    test()
