import yfinance as yf

def test():
    indices = {
        "^NSEI": "NIFTY 50",
        "^CNX100": "NIFTY 100",
        "^NSEBANK": "BANK NIFTY",
        "^INDIAVIX": "India VIX"
    }

    for symbol, name in indices.items():
        print(f"\n--- Testing {name} ({symbol}) ---")
        ticker = yf.Ticker(symbol)
        try:
            fast = ticker.fast_info
            print(f"Fast Info Price: {getattr(fast, 'last_price', 'N/A')}")
            print(f"Fast Info Prev Close: {getattr(fast, 'previous_close', 'N/A')}")
        except Exception as e:
            print(f"Fast Info Error: {e}")

        try:
            info = ticker.info
            print(f"Standard Info Price: {info.get('regularMarketPrice', 'N/A')}")
            print(f"Standard Info Prev Close: {info.get('regularMarketPreviousClose', 'N/A')}")
        except Exception as e:
            print(f"Standard Info Error: {e}")

if __name__ == "__main__":
    test()
