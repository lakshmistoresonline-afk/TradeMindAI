import joblib
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
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
        Enterprise Training Pipeline with Platt Scaling Calibration.
        """
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss, log_loss

        if len(features) < 150:
            raise ValueError(f"Insufficient features for calibrated training ({len(features)})")

        # 1. Prepare Data
        df = pd.DataFrame([{"date": f.date, **f.features, "target": f.target} for f in features])
        df.sort_values('date', inplace=True)
        df.set_index('date', inplace=True)

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)

        if len(df) < 100:
             raise ValueError(f"Insufficient valid samples after cleaning ({len(df)})")

        X = df.drop('target', axis=1)
        y = df['target'].astype(int)
        feature_names = list(X.columns)

        # 2. Chronological Split
        n = len(df)
        train_end = int(n * 0.6)
        calib_end = int(n * 0.8)

        X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
        X_calib, y_calib = X.iloc[train_end:calib_end], y.iloc[train_end:calib_end]
        X_test, y_test = X.iloc[calib_end:], y.iloc[calib_end:]

        # 3. Fit
        model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=10, random_state=42, class_weight='balanced')
        model.fit(X_train, y_train)

        # 4. Calibrate
        probs_calib = model.predict_proba(X_calib)[:, 1].reshape(-1, 1)
        calibrator = LogisticRegression(C=1e10)
        calibrator.fit(probs_calib, y_calib)

        calib_params = {"slope": float(calibrator.coef_[0][0]), "intercept": float(calibrator.intercept_[0])}

        # 5. Evaluate
        if len(np.unique(y_test)) > 1:
            probs_test_raw = model.predict_proba(X_test)[:, 1]
            probs_test_calibrated = calibrator.predict_proba(probs_test_raw.reshape(-1, 1))[:, 1]
            y_pred = (probs_test_calibrated > 0.5).astype(int)

            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, zero_division=0))
            rec = float(recall_score(y_test, y_pred, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, zero_division=0))
            auc = float(roc_auc_score(y_test, probs_test_calibrated))
            brier_raw = float(brier_score_loss(y_test, probs_test_raw))
            brier_calib = float(brier_score_loss(y_test, probs_test_calibrated))
            logloss_calib = float(log_loss(y_test, probs_test_calibrated))
        else:
            acc, prec, rec, f1, auc = 0.5, 0.0, 0.0, 0.0, 0.5
            brier_raw, brier_calib, logloss_calib = 0.25, 0.25, 0.69

        # 6. Save
        importances = {k: float(v) for k, v in zip(X.columns, model.feature_importances_)}
        version = datetime.utcnow().strftime("%Y%m%d%H%M")
        model_name = f"{symbol}_rf_{version}.joblib"
        calibrator_name = f"{symbol}_platt_{version}.joblib"

        joblib.dump(model, os.path.join(self.model_dir, model_name))
        joblib.dump(calibrator, os.path.join(self.model_dir, calibrator_name))

        # 7. Metadata
        print(f"      [DEBUG] {symbol} Metadata creation...")
        m_data = {
            "name": model_name,
            "symbol": symbol,
            "version": version,
            "type": "RANDOM_FOREST",
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": auc,
            "brier_score": brier_calib,
            "is_champion": False,
            "status": "CANDIDATE",
            "last_trained": datetime.utcnow(),
            "hyperparameters": {"n_estimators": 100, "feature_names": feature_names},
            "feature_importances": importances,
            "calibration_metadata": {
                "method": "platt_scaling",
                "calibrator_file": calibrator_name,
                "brier_score_raw": brier_raw,
                "brier_score_calibrated": brier_calib,
                "log_loss_calibrated": logloss_calib,
                "params": calib_params
            }
        }

        # Verify no None values for mandatory fields
        for k, v in m_data.items():
             if v is None:
                  print(f"      [CRITICAL] Field {k} is None!")

        metadata = ModelMetadata(**m_data)

        current_champion = await self.repository.get_champion_model(symbol)
        if not current_champion or brier_calib < current_champion.brier_score:
            metadata.is_champion = True
            metadata.status = "CHAMPION"
            if current_champion:
                current_champion.is_champion = False
                current_champion.status = "CHALLENGER"
                await self.repository.save_model_metadata(current_champion)

        await self.repository.save_model_metadata(metadata)
        return metadata

    async def predict_with_champion(self, symbol: str, feature_vector: Dict[str, float], champion: Optional[ModelMetadata] = None, save: bool = True) -> Dict[str, Any]:
        if champion is None:
            champion = await self.repository.get_champion_model(symbol)

        if not champion:
            return {"prediction": "N/A", "confidence": 0, "model_version": "none"}

        model_path = os.path.join(self.model_dir, champion.name)
        if not os.path.exists(model_path):
            return {"prediction": "ERROR", "confidence": 0, "error": "Model file missing"}

        model = joblib.load(model_path)
        calibrator = None
        if champion.calibration_metadata and "calibrator_file" in champion.calibration_metadata:
            calibrator_path = os.path.join(self.model_dir, champion.calibration_metadata["calibrator_file"])
            if os.path.exists(calibrator_path):
                calibrator = joblib.load(calibrator_path)

        feature_names = champion.hyperparameters.get("feature_names")
        X_input = pd.DataFrame([feature_vector])[feature_names] if feature_names else pd.DataFrame([feature_vector])

        raw_prob = float(model.predict_proba(X_input)[0][1])
        calibrated_prob = float(calibrator.predict_proba(np.array([[raw_prob]])) [0][1]) if calibrator else raw_prob

        prediction_label = "UP" if calibrated_prob > 0.55 else "DOWN" if calibrated_prob < 0.45 else "NEUTRAL"

        prediction = Prediction(
            symbol=symbol,
            date=datetime.utcnow(),
            model_version=champion.version,
            prediction=prediction_label,
            probability=float(calibrated_prob),
            confidence=float(calibrated_prob if calibrated_prob > 0.5 else 1-calibrated_prob),
            metadata={
                "calibrated_probability_up": float(calibrated_prob),
                "raw_probability_up": float(raw_prob),
                "is_calibrated": calibrator is not None
            }
        )
        if save:
            await self.repository.save_prediction(prediction)

        return {
            "prediction": prediction_label,
            "confidence": round(prediction.confidence * 100, 2),
            "model_version": champion.version,
            "is_calibrated": calibrator is not None,
            "metadata": prediction.metadata
        }
