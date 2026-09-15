from typing import Dict, Any, List, Optional
from backend.domain.models.data_platform import FeatureVector, FeatureDefinition
from backend.domain.interfaces.repository import IDataPlatformRepository
from datetime import datetime

class FeatureStoreService:
    def __init__(self, repository: IDataPlatformRepository):
        self.repository = repository
        self.current_version = "v1.0.0"
        self.registry: Dict[str, FeatureDefinition] = {}

    async def initialize_registry(self):
        """
        Loads feature definitions from the repository or creates defaults.
        """
        defs = await self.repository.get_feature_definitions()
        if defs:
            self.registry = {d.name: d for d in defs}
        else:
            await self._create_default_definitions()

    async def _create_default_definitions(self):
        defaults = [
            # Technical
            FeatureDefinition(name="trend_ema_cross", description="EMA 20 > EMA 50", category="TECHNICAL", data_type="BOOLEAN", version=self.current_version),
            FeatureDefinition(name="momentum_rsi", description="RSI scaled 0-1", category="TECHNICAL", data_type="FLOAT", min_value=0.0, max_value=1.0, version=self.current_version),
            FeatureDefinition(name="volatility_bb", description="Distance from Bollinger Bands", category="TECHNICAL", data_type="FLOAT", version=self.current_version),
            FeatureDefinition(name="volume_relative", description="Relative volume vs 20d mean", category="QUANTITATIVE", data_type="FLOAT", version=self.current_version),

            # SMC / ICT
            FeatureDefinition(name="smc_bullish_ob", description="Presence of Bullish Order Block", category="SMC", data_type="BOOLEAN", version=self.current_version),
            FeatureDefinition(name="smc_bearish_ob", description="Presence of Bearish Order Block", category="SMC", data_type="BOOLEAN", version=self.current_version),
            FeatureDefinition(name="ict_liquidity_void", description="Detection of price gap / liquidity void", category="ICT", data_type="BOOLEAN", version=self.current_version),

            # Wyckoff / Wave
            FeatureDefinition(name="wyckoff_phase", description="Current Wyckoff Cycle phase", category="WYCKOFF", data_type="STRING", version=self.current_version),
            FeatureDefinition(name="elliott_count", description="Current major wave count", category="ELLIOTT", data_type="INT", version=self.current_version),

            # Institutional
            FeatureDefinition(name="fii_net_bias", description="Standardized FII net flow bias", category="INSTITUTIONAL", data_type="FLOAT", version=self.current_version),
        ]
        for d in defaults:
            await self.repository.save_feature_definition(d)
            self.registry[d.name] = d

    async def validate_features(self, features: Dict[str, float]) -> List[str]:
        """
        Enterprise Feature Validation logic.
        """
        errors = []
        for name, value in features.items():
            if name not in self.registry:
                # Log new feature discovery
                continue

            d = self.registry[name]
            if isinstance(value, (int, float)):
                if d.min_value is not None and value < d.min_value:
                    errors.append(f"{name}: {value} < min {d.min_value}")
                if d.max_value is not None and value > d.max_value:
                    errors.append(f"{name}: {value} > max {d.max_value}")

        return errors

    async def ingest_features(self, symbol: str, date: datetime, features: Dict[str, Any]):
        errors = await self.validate_features(features)
        if errors:
            print(f"Feature Audit Alert [{symbol}]: {errors}")

        vector = FeatureVector(
            symbol=symbol,
            date=date,
            version=self.current_version,
            features={k: v for k, v in features.items() if isinstance(v, (int, float, bool))},
            metadata={"raw": features} # Store non-float metadata like strings
        )
        await self.repository.save_feature_vector(vector)

    def extract_institutional_features(self, df_ta: Any, smc_data: Dict[str, Any], timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Canonical Time-Safe Feature Engineering.
        Vision 2.2 Hardening: Removed accuracy-damaging constant fallbacks.
        """
        if df_ta is None or df_ta.empty:
            return {}

        import pandas as pd
        import math
        import numpy as np

        # 1. TIME-SAFE SLICING
        if timestamp:
            df_ta = df_ta[df_ta.index <= timestamp]
            if df_ta.empty: return {}

        last_row = df_ta.iloc[-1]
        data_ts = df_ta.index[-1]

        # Resilient value extractor (returns NaN instead of 0.0 for missing data)
        def get_val(key):
            # Try exact, then capitalized, then uppercase
            for k in [key, key.capitalize(), key.upper()]:
                if k in last_row:
                    val = last_row.get(k)
                    if val is not None and not (isinstance(val, float) and math.isnan(val)):
                        return float(val)
            return np.nan

        close = get_val("Close")

        # Core Technical Features
        features = {
            "Close": close,
            "High": get_val("High"),
            "Low": get_val("Low"),
            "ATR": get_val("ATR"),
            "natr": get_val("natr"),
            "ema_20": get_val("ema_20"),
            "ema_50": get_val("ema_50"),
            "ema_100": get_val("ema_100"),
            "ema_200": get_val("ema_200"),
            "ema_20_slope": get_val("ema_20_slope"),
            "ema_200_slope": get_val("ema_200_slope"),
            "sma_20": get_val("sma_20"),
            "momentum_rsi": get_val("momentum_rsi"),
            "momentum_roc": get_val("momentum_roc"),
            "macd": get_val("macd"),
            "macd_hist": get_val("macd_hist"),
            "stoch_k": get_val("stoch_k"),
            "momentum_cci": get_val("momentum_cci"),
            "adx": get_val("adx"),
            "dmp": get_val("dmp"),
            "dmn": get_val("dmn"),
            "volatility_bb_width": get_val("volatility_bb_width"),
            "volatility_bb_pct": get_val("volatility_bb_pct"),
            "hist_vol": get_val("hist_vol"),
            "volume_relative": get_val("volume_relative"),
            "obv": get_val("obv"),
            "mfi": get_val("mfi"),
            "trend_ema_cross": get_val("trend_ema_cross"),
            "market_volatility_z": get_val("market_volatility_z"),
            "market_cap_class": get_val("market_cap_class"),
        }

        # Derived distance features
        if not math.isnan(close):
            if not math.isnan(features["ema_200"]):
                features["dist_ema_200"] = (close - features["ema_200"]) / features["ema_200"]
            if not math.isnan(features["sma_20"]):
                features["dist_sma_20"] = (close - features["sma_20"]) / features["sma_20"]

        return features

    async def find_similar_patterns(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Vision 2.0: AI Similarity Engine.
        Finds historical periods with similar feature vectors.
        [FORENSIC_UPDATE]: Hardcoded patterns removed. Implementation pending valid similarity engine.
        """
        return []

    async def update_features(self, symbol: str):
        """
        Retrieves recent prices, calculates technical indicators,
        extracts model features and persists to analytical engine.
        """
        from backend.analysis.technical import TechnicalAnalysis
        from backend.core.container import container
        import pandas as pd

        # 1. Fetch recent prices
        recent_prices = await container.repository.get_recent_prices(symbol, limit=500)
        if not recent_prices:
            return

        # 2. Convert to DataFrame
        # Skip conversion if already a DF? No, get_recent_prices returns list of StockPrice
        df = pd.DataFrame([p.model_dump() for p in recent_prices])
        if df.empty: return

        print(f"      [DEBUG] {symbol} Prices fetched: {len(df)}")

        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)

        # 3. Calculate Technical Indicators
        df_ta = TechnicalAnalysis.calculate_indicators(df)
        print(f"      [DEBUG] {symbol} Indicators calculated. Tail Close: {df_ta['Close'].iloc[-1]}")

        # 5. Optimized: Just ingest the last row for now (Production Refresh)
        last_row_features = self.extract_institutional_features(df_ta, smc_data={}, timestamp=df_ta.index[-1])

        await self.ingest_features(symbol, df_ta.index[-1], last_row_features)
