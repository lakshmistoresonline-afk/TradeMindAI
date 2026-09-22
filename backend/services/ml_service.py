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

    async def train_and_register(self, symbol: str, features: List[FeatureVector], horizon: str = "SWING") -> ModelMetadata:
        """
        Enterprise Training Pipeline with Platt Scaling Calibration.
        Phase 8: Horizon-Specific Specialization.
        Implemented: Chronological Walk-Forward and Calibration.
        """
        from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss, log_loss

        if len(features) < 100:
            raise ValueError(f"Insufficient features for training ({len(features)})")

        # 1. Prepare Data
        df = pd.DataFrame([{"date": f.date, **f.features, "target": f.target} for f in features])
        df.sort_values('date', inplace=True)
        df.set_index('date', inplace=True)

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows where target is NaN (happens at end of series)
        df = df.dropna(subset=['target'])
        df = df.fillna(0) # Fill feature NaNs with 0 for model stability

        if len(df) < 80:
             raise ValueError(f"Insufficient valid samples after cleaning ({len(df)})")

        X = df.drop('target', axis=1)
        y = df['target'].astype(int)
        feature_names = list(X.columns)

        # 2. Chronological Split (Walk-Forward)
        n = len(df)
        train_end = int(n * 0.7)
        calib_end = int(n * 0.85)

        X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
        X_calib, y_calib = X.iloc[train_end:calib_end], y.iloc[train_end:calib_end]
        X_test, y_test = X.iloc[calib_end:], y.iloc[calib_end:]

        # 3. Multi-Model Soft Voting Ensemble (Phase 4)
        from sklearn.ensemble import VotingClassifier, RandomForestClassifier

        gb_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
        et_model = ExtraTreesClassifier(n_estimators=100, max_depth=7, random_state=42, class_weight='balanced')
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight='balanced')

        model = VotingClassifier(
            estimators=[('gb', gb_model), ('et', et_model), ('rf', rf_model)],
            voting='soft'
        )

        model.fit(X_train, y_train)

        # 4. Calibration (Isotonic Regression with Platt Scaling Fallback)
        from sklearn.isotonic import IsotonicRegression
        from backend.services.calibration_service import CalibrationService

        probs_calib = model.predict_proba(X_calib)[:, 1]

        # Use Isotonic Regression when sample size is adequate, otherwise Logistic Regression
        use_isotonic = len(y_calib) >= 30 and len(np.unique(y_calib)) > 1
        if use_isotonic:
            calibrator = IsotonicRegression(out_of_bounds='clip')
            calibrator.fit(probs_calib, y_calib)
            calib_params = {"method": "isotonic", "samples": len(y_calib)}
        else:
            calibrator = LogisticRegression(C=1e10)
            calibrator.fit(probs_calib.reshape(-1, 1), y_calib)
            calib_params = {"slope": float(calibrator.coef_[0][0]), "intercept": float(calibrator.intercept_[0])}

        # 5. Evaluate on OOS (Test) Set
        if len(np.unique(y_test)) > 1:
            probs_test_raw = model.predict_proba(X_test)[:, 1]
            if use_isotonic:
                probs_test_calibrated = calibrator.predict(probs_test_raw)
            else:
                probs_test_calibrated = calibrator.predict_proba(probs_test_raw.reshape(-1, 1))[:, 1]

            y_pred = (probs_test_calibrated > 0.5).astype(int)

            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, zero_division=0))
            rec = float(recall_score(y_test, y_pred, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, zero_division=0))
            auc = float(roc_auc_score(y_test, probs_test_calibrated))
            brier_calib = float(brier_score_loss(y_test, probs_test_calibrated))
            logloss_calib = float(log_loss(y_test, probs_test_calibrated))
            ece_val = CalibrationService.calculate_expected_calibration_error(y_test.values, probs_test_calibrated)
        else:
            acc, prec, rec, f1, auc = 0.5, 0.0, 0.0, 0.0, 0.5
            brier_calib, logloss_calib, ece_val = 0.25, 0.69, 0.0

        # 6. Save
        version = f"v2.3_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        model_name = f"{symbol}_{horizon}_model_{version}.joblib"
        calibrator_name = f"{symbol}_{horizon}_calib_{version}.joblib"

        joblib.dump(model, os.path.join(self.model_dir, model_name))
        joblib.dump(calibrator, os.path.join(self.model_dir, calibrator_name))

        # Compute ensemble feature importances
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        else:
            try:
                base_imps = [est.feature_importances_ for name, est in model.named_estimators_.items() if hasattr(est, "feature_importances_")]
                importances = np.mean(base_imps, axis=0) if base_imps else np.zeros(len(X.columns))
            except Exception:
                importances = np.zeros(len(X.columns))

        # 7. Metadata
        m_data = {
            "name": model_name,
            "symbol": symbol,
            "version": version,
            "horizon": horizon,
            "type": str(type(model).__name__),
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": auc,
            "brier_score": brier_calib,
            "is_champion": True, # Automatically champion for new horizon
            "status": "CHAMPION",
            "last_trained": datetime.utcnow(),
            "hyperparameters": {
                "feature_names": feature_names,
                "horizon": horizon,
                "train_size": len(X_train),
                "test_size": len(X_test),
                "positives_test": int(y_test.sum())
            },
            "feature_importances": {k: float(v) for k, v in zip(X.columns, importances)},
            "calibration_metadata": {
                "method": "isotonic" if use_isotonic else "platt_scaling",
                "calibrator_file": calibrator_name,
                "brier_score_calibrated": brier_calib,
                "log_loss_calibrated": logloss_calib,
                "params": calib_params,
                "ece": ece_val
            }
        }

        metadata = ModelMetadata(**m_data)
        await self.repository.save_model_metadata(metadata)
        return metadata

    async def predict_with_champion(self, symbol: str, feature_vector: Dict[str, float], horizon: str = "SWING", champion: Optional[ModelMetadata] = None, save: bool = True) -> Dict[str, Any]:
        if champion is None:
            champion = await self.repository.get_champion_model(symbol, horizon=horizon)

        if not champion:
             # V2.3 Local Resilience: Return mock if no record exists in dev mode
            if os.getenv("ENVIRONMENT") == "development":
                return self._generate_mock_prediction(symbol, horizon)
            return {"prediction": "N/A", "confidence": 0, "model_version": "none"}

        model_path = os.path.join(self.model_dir, champion.name)
        if not os.path.exists(model_path):
            # V2.3 Local Resilience: Return mock if DB record exists but file is missing
            if os.getenv("ENVIRONMENT") == "development":
                return self._generate_mock_prediction(symbol, horizon, champion.version)
            return {"prediction": "ERROR", "confidence": 0, "error": "Model file missing"}

        model = joblib.load(model_path)
        calibrator = None
        if champion.calibration_metadata and "calibrator_file" in champion.calibration_metadata:
            calibrator_path = os.path.join(self.model_dir, champion.calibration_metadata["calibrator_file"])
            if os.path.exists(calibrator_path):
                calibrator = joblib.load(calibrator_path)

        feature_names = champion.hyperparameters.get("feature_names")
        X_input = pd.DataFrame([feature_vector])
        if feature_names:
            X_input = X_input.reindex(columns=feature_names)

        X_input = X_input.fillna(0) # Phase 4 Hardening: Handle NaNs in inference

        raw_prob = float(model.predict_proba(X_input)[0][1])
        calibrated_prob = CalibrationService.calibrate_isotonic(raw_prob, calibrator_model=calibrator)

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

    @staticmethod
    def select_top_features_via_shap(X: pd.DataFrame, y: pd.Series, top_n: int = 15) -> List[str]:
        """
        Phase 5: TreeSHAP Feature Selection / Noise Pruning.
        Uses TreeSHAP or ensemble feature importances to select top N uninformative-pruned features.
        """
        try:
            import shap
            from sklearn.ensemble import ExtraTreesClassifier
            model = ExtraTreesClassifier(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X, y)
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)

            if isinstance(shap_values, list):
                shap_values = shap_values[1]

            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            imp_series = pd.Series(mean_abs_shap, index=X.columns).sort_values(ascending=False)
            return imp_series.head(top_n).index.tolist()
        except Exception:
            from sklearn.ensemble import ExtraTreesClassifier
            model = ExtraTreesClassifier(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X, y)
            imp_series = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
            return imp_series.head(top_n).index.tolist()

    @staticmethod
    def purged_cross_validation_score(model: Any, X: pd.DataFrame, y: pd.Series, cv_folds: int = 5, embargo_pct: float = 0.05) -> Dict[str, float]:
        """
        Phase 5: Marcos López de Prado Purged Group CV with Embargoing.
        Eliminates time-series label overlap leakage.
        """
        from sklearn.metrics import accuracy_score, roc_auc_score

        n = len(X)
        fold_size = n // cv_folds
        embargo_size = int(n * embargo_pct)

        scores = []
        aucs = []

        for i in range(cv_folds):
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < cv_folds - 1 else n

            test_idx = list(range(test_start, test_end))

            train_idx = list(range(0, max(0, test_start - 1))) + list(range(min(n, test_end + embargo_size), n))

            if not train_idx or not test_idx:
                continue

            X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
            X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

            if len(np.unique(y_train)) < 2 or len(np.unique(y_test)) < 2:
                continue

            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1]

            scores.append(accuracy_score(y_test, preds))
            aucs.append(roc_auc_score(y_test, probs))

        return {
            "purged_cv_accuracy": round(float(np.mean(scores)) if scores else 0.5, 4),
            "purged_cv_auc": round(float(np.mean(aucs)) if aucs else 0.5, 4),
            "folds_evaluated": len(scores)
        }

    @staticmethod
    def tune_hyperparameters_optuna(X: pd.DataFrame, y: pd.Series, n_trials: int = 10) -> Dict[str, Any]:
        """
        Phase 5: Optuna / Randomized Search Hyperparameter Optimization.
        Tunes n_estimators, max_depth, learning_rate, and sub-sample sizes.
        """
        try:
            import optuna
            optuna.logging.set_verbosity(optuna.logging.WARNING)

            def objective(trial):
                n_est = trial.suggest_int('n_estimators', 50, 150, step=25)
                max_d = trial.suggest_int('max_depth', 3, 7)
                lr = trial.suggest_float('learning_rate', 0.02, 0.15, log=True)

                from sklearn.ensemble import GradientBoostingClassifier
                from sklearn.model_selection import cross_val_score
                clf = GradientBoostingClassifier(n_estimators=n_est, max_depth=max_d, learning_rate=lr, random_state=42)
                return float(np.mean(cross_val_score(clf, X, y, cv=3, scoring='roc_auc')))

            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=min(n_trials, 8))
            return study.best_params
        except Exception:
            from sklearn.model_selection import RandomizedSearchCV
            from sklearn.ensemble import GradientBoostingClassifier
            param_grid = {'n_estimators': [50, 100, 150], 'max_depth': [3, 4, 6], 'learning_rate': [0.03, 0.05, 0.1]}
            clf = GradientBoostingClassifier(random_state=42)
            search = RandomizedSearchCV(clf, param_distributions=param_grid, n_iter=4, cv=3, random_state=42)
            search.fit(X, y)
            return search.best_params_

    def _generate_mock_prediction(self, symbol: str, horizon: str, version: str = "v2.2-local-mock") -> Dict[str, Any]:
        """
        Generates a stable, high-conviction BUY signal for local testing and population.
        """
        calibrated_prob = 0.82
        raw_prob = 0.80
        prediction_label = "UP"

        return {
            "prediction": prediction_label,
            "confidence": 85.0,
            "model_version": version,
            "is_calibrated": True,
            "metadata": {
                "calibrated_probability_up": calibrated_prob,
                "raw_probability_up": raw_prob,
                "is_calibrated": True,
                "mock_generated": True
            }
        }
