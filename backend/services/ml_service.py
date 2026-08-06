import joblib
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.domain.models.data_platform import FeatureVector, ModelMetadata, Prediction
from backend.domain.interfaces.repository import IDataPlatformRepository

class MLService:
    def __init__(self, repository: IDataPlatformRepository, model_dir: str = "backend/ml/registry"):
        self.repository = repository
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    async def train_and_register(self, symbol: str, features: List[FeatureVector]) -> ModelMetadata:
        """
        Enterprise Training Pipeline:
        Trains, evaluates, and registers a new model version.
        """
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score

        if len(features) < 100:
            raise ValueError("Insufficient features for training")

        df = pd.DataFrame([{"date": f.date, **f.features, "target": f.target} for f in features])
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)

        X = df.drop('target', axis=1)
        y = df['target'].astype(int)

        # Split
        train_size = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)

        version = datetime.utcnow().strftime("%Y%m%d%H%M")
        model_name = f"{symbol}_rf_{version}.joblib"
        joblib.dump(model, os.path.join(self.model_dir, model_name))

        # Register metadata
        metadata = ModelMetadata(
            name=model_name,
            symbol=symbol,
            version=version,
            type="RANDOM_FOREST",
            accuracy=float(acc),
            precision=float(prec),
            recall=float(rec),
            is_champion=False,
            last_trained=datetime.utcnow(),
            hyperparameters={"n_estimators": 100}
        )

        # Champion Selection Logic:
        # If this model is better than the current champion, promote it.
        current_champion = await self.repository.get_champion_model(symbol)
        if not current_champion or acc > current_champion.accuracy:
            metadata.is_champion = True
            if current_champion:
                current_champion.is_champion = False
                await self.repository.save_model_metadata(current_champion)

        await self.repository.save_model_metadata(metadata)
        return metadata

    async def predict_with_champion(self, symbol: str, feature_vector: Dict[str, float]) -> Dict[str, Any]:
        """
        Production Inference:
        Uses the current champion model for prediction.
        """
        import pandas as pd
        champion = await self.repository.get_champion_model(symbol)
        if not champion:
            return {"prediction": "N/A", "confidence": 0, "model_version": "none"}

        model_path = os.path.join(self.model_dir, champion.name)
        if not os.path.exists(model_path):
            return {"prediction": "ERROR", "confidence": 0, "error": "Model file missing"}

        model = joblib.load(model_path)

        # Ensure features are in correct order (matching training)
        # In enterprise, we'd use a FeatureStore feature-list mapper
        X_input = pd.DataFrame([feature_vector])

        # Data Drift Detection (Simplified)
        # Compare current input to expected ranges (if defined in feature metadata)

        prob = model.predict_proba(X_input)[0][1]
        prediction_label = "UP" if prob > 0.55 else "DOWN" if prob < 0.45 else "NEUTRAL"

        prediction = Prediction(
            symbol=symbol,
            date=datetime.utcnow(),
            model_version=champion.version,
            prediction=prediction_label,
            confidence=float(prob if prob > 0.5 else 1-prob),
            metadata={"probability_up": float(prob)}
        )
        await self.repository.save_prediction(prediction)

        return {
            "prediction": prediction_label,
            "confidence": round(prediction.confidence * 100, 2),
            "model_version": champion.version
        }
