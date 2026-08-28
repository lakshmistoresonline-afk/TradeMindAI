import pandas as pd
from backend.analysis.smc import SMCAnalysis

def test_detect_order_blocks():
    # Create a scenario for a bullish order block
    # Bullish OB: Down candle before a strong up move
    data = {
        "Open": [100, 95, 105, 110],
        "Close": [95, 105, 110, 115],
        "High": [101, 106, 111, 116],
        "Low": [94, 94, 104, 109],
        "Volume": [1000, 5000, 5000, 5000]
    }
    df = pd.DataFrame(data)

    obs = SMCAnalysis.detect_order_blocks(df)

    # In our simplified logic, index 1 (Open 95, Close 105) followed by strong move
    # should be detected if the criteria match.
    # Note: Logic in smc.py uses: if df["Close"].iloc[i+1] > df["High"].iloc[i] * 1.02:
    # 110 > 106 * 1.02 (108.12) -> True.
    # Open[1] 95 > Close[1] 105 -> False (Not a down candle)

    # Let's create a better mock for a down candle followed by a spike
    data_v2 = {
        "Open": [100, 100, 110, 120], # Down candle at idx 1
        "Close": [105, 95, 120, 130],
        "High": [106, 101, 121, 131],
        "Low": [99, 94, 109, 119],
        "Volume": [1000, 1000, 5000, 5000]
    }
    df_v2 = pd.DataFrame(data_v2)
    obs_v2 = SMCAnalysis.detect_order_blocks(df_v2)

    assert len(obs_v2) > 0
    assert obs_v2[0]["type"] == "bullish"

def test_detect_fvg():
    # Bullish FVG: Low of candle 3 is higher than High of candle 1
    data = {
        "High": [100, 110, 120],
        "Low": [90, 105, 115] # Low of idx 2 (115) > High of idx 0 (100)
    }
    df = pd.DataFrame(data)

    fvgs = SMCAnalysis.detect_fvg(df)

    assert len(fvgs) > 0
    assert fvgs[0]["type"] == "bullish"
