"""
ML Model training for test selection
"""
import pandas as pd
import numpy as np
import sys
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)
import joblib
from typing import Dict, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.feature_extractor import FeatureExtractor


class ModelTrainer:
    """Trains ML models for test failure prediction"""

    def __init__(self, algorithm: str = 'random_forest', **kwargs):
        self.algorithm = algorithm
        self.model = self._create_model(algorithm, **kwargs)
        self.feature_extractor = FeatureExtractor()
        self.is_trained = False

    def _create_model(self, algorithm: str, **kwargs):
        """Create ML model based on algorithm"""
        if algorithm == 'random_forest':
            return RandomForestClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                random_state=kwargs.get('random_state', 42),
                n_jobs=-1
            )
        elif algorithm == 'gradient_boosting':
            return GradientBoostingClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 5),
                random_state=kwargs.get('random_state', 42)
            )
        elif algorithm == 'logistic_regression':
            return LogisticRegression(
                random_state=kwargs.get('random_state', 42),
                max_iter=1000
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        Train the model on test execution history
        Returns training metrics
        """
        print(f"Training {self.algorithm} model...")

        # Extract features
        print("Extracting features...")
        features_df = self.feature_extractor.extract_features(df)

        # Prepare target variable (1 = failed, 0 = passed)
        y = (~df['passed']).astype(int)

        # Remove any rows with NaN values
        mask = ~(features_df.isna().any(axis=1) | y.isna())
        features_df = features_df[mask]
        y = y[mask]

        # Scale features
        print("Scaling features...")
        X = self.feature_extractor.fit_transform(features_df)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        print(f"Failure rate: {y.mean():.2%}")

        # Train model
        print("Training model...")
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate
        print("Evaluating model...")
        metrics = self._evaluate_model(X_train, X_test, y_train, y_test)

        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(zip(
                self.feature_extractor.feature_names,
                self.model.feature_importances_
            ))
            metrics['feature_importance'] = feature_importance

        return metrics

    def _evaluate_model(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """Evaluate model performance"""
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)

        # Probabilities for ROC-AUC
        if hasattr(self.model, 'predict_proba'):
            y_train_proba = self.model.predict_proba(X_train)[:, 1]
            y_test_proba = self.model.predict_proba(X_test)[:, 1]
        else:
            y_train_proba = y_train_pred
            y_test_proba = y_test_pred

        # Calculate metrics
        metrics = {
            'train_accuracy': accuracy_score(y_train, y_train_pred),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'train_precision': precision_score(y_train, y_train_pred, zero_division=0),
            'test_precision': precision_score(y_test, y_test_pred, zero_division=0),
            'train_recall': recall_score(y_train, y_train_pred, zero_division=0),
            'test_recall': recall_score(y_test, y_test_pred, zero_division=0),
            'train_f1': f1_score(y_train, y_train_pred, zero_division=0),
            'test_f1': f1_score(y_test, y_test_pred, zero_division=0),
            'train_roc_auc': roc_auc_score(y_train, y_train_proba),
            'test_roc_auc': roc_auc_score(y_test, y_test_proba)
        }

        # Print results
        print("\n" + "="*50)
        print("MODEL PERFORMANCE")
        print("="*50)
        print(f"\nTrain Accuracy: {metrics['train_accuracy']:.4f}")
        print(f"Test Accuracy:  {metrics['test_accuracy']:.4f}")
        print(f"\nTrain Precision: {metrics['train_precision']:.4f}")
        print(f"Test Precision:  {metrics['test_precision']:.4f}")
        print(f"\nTrain Recall: {metrics['train_recall']:.4f}")
        print(f"Test Recall:  {metrics['test_recall']:.4f}")
        print(f"\nTrain F1: {metrics['train_f1']:.4f}")
        print(f"Test F1:  {metrics['test_f1']:.4f}")
        print(f"\nTrain ROC-AUC: {metrics['train_roc_auc']:.4f}")
        print(f"Test ROC-AUC:  {metrics['test_roc_auc']:.4f}")
        print("="*50 + "\n")

        return metrics

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict:
        """Perform cross-validation"""
        print(f"Performing {cv}-fold cross-validation...")

        scores = {
            'accuracy': cross_val_score(self.model, X, y, cv=cv, scoring='accuracy'),
            'precision': cross_val_score(self.model, X, y, cv=cv, scoring='precision', error_score='raise'),
            'recall': cross_val_score(self.model, X, y, cv=cv, scoring='recall', error_score='raise'),
            'f1': cross_val_score(self.model, X, y, cv=cv, scoring='f1', error_score='raise')
        }

        results = {
            'accuracy_mean': scores['accuracy'].mean(),
            'accuracy_std': scores['accuracy'].std(),
            'precision_mean': scores['precision'].mean(),
            'precision_std': scores['precision'].std(),
            'recall_mean': scores['recall'].mean(),
            'recall_std': scores['recall'].std(),
            'f1_mean': scores['f1'].mean(),
            'f1_std': scores['f1'].std()
        }

        print(f"Accuracy: {results['accuracy_mean']:.4f} (+/- {results['accuracy_std']:.4f})")
        print(f"Precision: {results['precision_mean']:.4f} (+/- {results['precision_std']:.4f})")
        print(f"Recall: {results['recall_mean']:.4f} (+/- {results['recall_std']:.4f})")
        print(f"F1: {results['f1_mean']:.4f} (+/- {results['f1_std']:.4f})")

        return results

    def predict_failure_probability(
        self,
        test_name: str,
        historical_data: pd.DataFrame,
        lines_changed: int = 0,
        functions_changed: int = 0
    ) -> float:
        """
        Predict probability of test failure
        Returns probability between 0 and 1
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")

        # Extract features for this test
        features = self.feature_extractor.extract_features_for_prediction(
            test_name, historical_data, lines_changed, functions_changed
        )

        # Scale features
        features_scaled = self.feature_extractor.transform(features)

        # Predict probability
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(features_scaled)[0, 1]
        else:
            # For models without predict_proba, use binary prediction
            proba = float(self.model.predict(features_scaled)[0])

        return proba

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores"""
        if not self.is_trained:
            return None

        if hasattr(self.model, 'feature_importances_'):
            importance = dict(zip(
                self.feature_extractor.feature_names,
                self.model.feature_importances_
            ))
            # Sort by importance
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        return None

    def save(self, model_path: str, scaler_path: str):
        """Save model and feature extractor"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(scaler_path), exist_ok=True)

        joblib.dump(self.model, model_path)
        self.feature_extractor.save(scaler_path)

        print(f"Model saved to: {model_path}")
        print(f"Feature extractor saved to: {scaler_path}")

    def load(self, model_path: str, scaler_path: str):
        """Load model and feature extractor"""
        self.model = joblib.load(model_path)
        self.feature_extractor.load(scaler_path)
        self.is_trained = True

        print(f"Model loaded from: {model_path}")
        print(f"Feature extractor loaded from: {scaler_path}")
