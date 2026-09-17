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
    # Needs many rows to reach the indices
    data_v2 = {
        "Open": [100]*25,
        "Close": [100]*25,
        "High": [100]*25,
        "Low": [100]*25,
        "Volume": [1000]*25
    }
    df_v2 = pd.DataFrame(data_v2)
    # Setup Bullish OB at index 14
    # (Last down candle before a displacement up)
    df_v2.iloc[14, 0] = 110 # Open
    df_v2.iloc[14, 1] = 100 # Close
    df_v2.iloc[14, 2] = 112 # High

    # Displacement up at index 15
    df_v2.iloc[15, 1] = 125 # 125 > 112 * 1.01 (113.12)

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
