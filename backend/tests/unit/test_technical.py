import pandas as pd
import numpy as np
from backend.analysis.technical import TechnicalAnalysis

def test_calculate_indicators():
    # Create dummy data
    data = {
        "Close": np.random.uniform(2400, 2500, 300),
        "High": np.random.uniform(2500, 2600, 300),
        "Low": np.random.uniform(2300, 2400, 300),
        "Volume": np.random.randint(100000, 1000000, 300)
    }
    df = pd.DataFrame(data)

    # Run analysis
    df_result = TechnicalAnalysis.calculate_indicators(df)

    # Verify indicators are present
    assert "ema_20" in df_result.columns
    assert "ema_50" in df_result.columns
    assert "ema_200" in df_result.columns
    assert "momentum_rsi" in df_result.columns

    # Verify no NaN values in latest row
    assert not np.isnan(df_result["ema_20"].iloc[-1])
    assert not np.isnan(df_result["momentum_rsi"].iloc[-1])

def test_calculate_volume_profile():
    data = {
        "Close": [100, 105, 110, 100, 105],
        "High": [110, 115, 120, 110, 115],
        "Low": [90, 95, 100, 90, 95],
        "Volume": [1000, 2000, 3000, 1000, 2000]
    }
    df = pd.DataFrame(data)

    result = TechnicalAnalysis.calculate_volume_profile(df, bins=5)

    assert "min" in result
    assert "max" in result
    assert "profile" in result
    assert len(result["profile"]) > 0
