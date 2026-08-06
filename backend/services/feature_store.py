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

    def extract_institutional_features(self, df_ta: Any, smc_data: Dict[str, Any], extra_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Refined Institutional Feature Engineering.
        """
        if df_ta is None or df_ta.empty:
            return {}

        import pandas as pd
        last_row = df_ta.iloc[-1]

        features = {
            # Core Technical
            "trend_ema_cross": float(last_row["EMA_20"] > last_row["EMA_50"]),
            "momentum_rsi": float(last_row["RSI"] / 100.0) if "RSI" in last_row else 0.5,
            "volatility_bb": float((last_row["Close"] - last_row["BBL_5_2.0"]) / (last_row["BBU_5_2.0"] - last_row["BBL_5_2.0"])) if (last_row.get("BBU_5_2.0") != last_row.get("BBL_5_2.0")) else 0.5,
            "volume_relative": float(last_row["Volume"] / df_ta["Volume"].tail(20).mean()) if df_ta["Volume"].tail(20).mean() != 0 else 1.0,

            # SMC Logic
            "smc_bullish_ob": float(any(ob["type"] == "bullish" for ob in smc_data.get("order_blocks", []))),
            "smc_bearish_ob": float(any(ob["type"] == "bearish" for ob in smc_data.get("order_blocks", []))),

            # ICT Concepts (Placeholder for expansion)
            "ict_liquidity_void": float(last_row.get("High") < df_ta["Low"].iloc[-2]) or float(last_row.get("Low") > df_ta["High"].iloc[-2]),

            # Contextual Data
            "market_cap_class": "LARGE" if last_row.get("market_cap", 0) > 2e11 else "MID" if last_row.get("market_cap", 0) > 5e9 else "SMALL",
        }

        return features
