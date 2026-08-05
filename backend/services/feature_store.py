import pandas as pd
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
            FeatureDefinition(name="trend_ema_cross", description="EMA 20 > EMA 50", category="TECHNICAL", data_type="BOOLEAN", version=self.current_version),
            FeatureDefinition(name="momentum_rsi", description="RSI scaled 0-1", category="TECHNICAL", data_type="FLOAT", min_value=0.0, max_value=1.0, version=self.current_version),
            FeatureDefinition(name="volatility_bb", description="Distance from Bollinger Bands", category="TECHNICAL", data_type="FLOAT", version=self.current_version),
            FeatureDefinition(name="volume_relative", description="Relative volume vs 20d mean", category="QUANTITATIVE", data_type="FLOAT", version=self.current_version),
            FeatureDefinition(name="smc_bullish_ob", description="Presence of Bullish Order Block", category="SMC", data_type="BOOLEAN", version=self.current_version),
            FeatureDefinition(name="smc_bearish_ob", description="Presence of Bearish Order Block", category="SMC", data_type="BOOLEAN", version=self.current_version),
        ]
        for d in defaults:
            await self.repository.save_feature_definition(d)
            self.registry[d.name] = d

    async def validate_features(self, features: Dict[str, float]) -> List[str]:
        """
        Validates features against their definitions in the registry.
        """
        errors = []
        for name, value in features.items():
            if name not in self.registry:
                errors.append(f"Feature {name} not found in registry")
                continue

            d = self.registry[name]
            if d.min_value is not None and value < d.min_value:
                errors.append(f"Feature {name} value {value} is below min {d.min_value}")
            if d.max_value is not None and value > d.max_value:
                errors.append(f"Feature {name} value {value} is above max {d.max_value}")

        return errors

    async def ingest_features(self, symbol: str, date: datetime, features: Dict[str, float]):
        """
        Validates and stores standardized feature vectors.
        """
        errors = await self.validate_features(features)
        if errors:
            print(f"Feature Ingestion Warning for {symbol}: {errors}")
            # In enterprise, we might stop ingestion or log to monitoring

        vector = FeatureVector(
            symbol=symbol,
            date=date,
            version=self.current_version,
            features=features
        )
        await self.repository.save_feature_vector(vector)

    def extract_ai_features(self, df_ta: pd.DataFrame, smc_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Institutional Feature Engineering.
        """
        last_row = df_ta.iloc[-1]

        features = {
            "trend_ema_cross": float(last_row["EMA_20"] > last_row["EMA_50"]),
            "momentum_rsi": float(last_row["RSI"] / 100.0),
            "volatility_bb": float((last_row["Close"] - last_row["BBL_5_2.0"]) / (last_row["BBU_5_2.0"] - last_row["BBL_5_2.0"])) if (last_row["BBU_5_2.0"] != last_row["BBL_5_2.0"]) else 0.5,
            "volume_relative": float(last_row["Volume"] / df_ta["Volume"].tail(20).mean()) if df_ta["Volume"].tail(20).mean() != 0 else 1.0,
            "smc_bullish_ob": float(any(ob["type"] == "bullish" for ob in smc_data.get("order_blocks", []))),
            "smc_bearish_ob": float(any(ob["type"] == "bearish" for ob in smc_data.get("order_blocks", []))),
        }

        return features
