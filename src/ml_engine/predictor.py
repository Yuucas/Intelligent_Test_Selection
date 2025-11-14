"""
Predictor for test selection
"""
import pandas as pd
import sys
import os
from typing import List, Dict, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.model_trainer import ModelTrainer


class TestFailurePredictor:
    """Predicts test failures for intelligent selection"""

    def __init__(self, model_path: str = None, scaler_path: str = None):
        self.trainer = ModelTrainer()

        if model_path and scaler_path:
            self.load_model(model_path, scaler_path)

    def load_model(self, model_path: str, scaler_path: str):
        """Load trained model"""
        self.trainer.load(model_path, scaler_path)

    def predict_test_failures(
        self,
        test_names: List[str],
        historical_data: pd.DataFrame,
        changed_files_map: Dict[str, Tuple[int, int]] = None
    ) -> Dict[str, float]:
        """
        Predict failure probability for multiple tests

        Args:
            test_names: List of test names to predict
            historical_data: Historical test execution data
            changed_files_map: Map of test_file -> (lines_changed, functions_changed)

        Returns:
            Dictionary mapping test names to failure probabilities
        """
        if changed_files_map is None:
            changed_files_map = {}

        predictions = {}

        for test_name in test_names:
            # Get change information for this test
            lines_changed = 0
            functions_changed = 0

            # Extract test file from full test name
            if '::' in test_name:
                test_file = test_name.split('::')[0]
                if test_file in changed_files_map:
                    lines_changed, functions_changed = changed_files_map[test_file]

            # Predict failure probability
            proba = self.trainer.predict_failure_probability(
                test_name,
                historical_data,
                lines_changed,
                functions_changed
            )

            predictions[test_name] = proba

        return predictions

    def rank_tests_by_failure_risk(
        self,
        test_names: List[str],
        historical_data: pd.DataFrame,
        changed_files_map: Dict[str, Tuple[int, int]] = None
    ) -> List[Tuple[str, float]]:
        """
        Rank tests by failure risk (highest first)

        Returns:
            List of tuples (test_name, failure_probability)
        """
        predictions = self.predict_test_failures(
            test_names, historical_data, changed_files_map
        )

        # Sort by probability (highest first)
        ranked = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

        return ranked

    def select_high_risk_tests(
        self,
        test_names: List[str],
        historical_data: pd.DataFrame,
        threshold: float = 0.5,
        changed_files_map: Dict[str, Tuple[int, int]] = None
    ) -> List[str]:
        """
        Select tests with failure probability above threshold

        Args:
            test_names: List of test names to evaluate
            historical_data: Historical test execution data
            threshold: Probability threshold (0.0 to 1.0)
            changed_files_map: Map of test_file -> (lines_changed, functions_changed)

        Returns:
            List of selected test names
        """
        predictions = self.predict_test_failures(
            test_names, historical_data, changed_files_map
        )

        selected = [
            test for test, proba in predictions.items()
            if proba >= threshold
        ]

        return selected

    def get_test_risk_summary(
        self,
        test_names: List[str],
        historical_data: pd.DataFrame,
        changed_files_map: Dict[str, Tuple[int, int]] = None
    ) -> Dict:
        """
        Get summary of test risk levels

        Returns:
            Dictionary with risk distribution
        """
        predictions = self.predict_test_failures(
            test_names, historical_data, changed_files_map
        )

        # Categorize by risk level
        high_risk = []    # > 0.7
        medium_risk = []  # 0.3 - 0.7
        low_risk = []     # < 0.3

        for test, proba in predictions.items():
            if proba > 0.7:
                high_risk.append((test, proba))
            elif proba > 0.3:
                medium_risk.append((test, proba))
            else:
                low_risk.append((test, proba))

        return {
            'total_tests': len(test_names),
            'high_risk': {
                'count': len(high_risk),
                'percentage': len(high_risk) / len(test_names) * 100,
                'tests': high_risk
            },
            'medium_risk': {
                'count': len(medium_risk),
                'percentage': len(medium_risk) / len(test_names) * 100,
                'tests': medium_risk
            },
            'low_risk': {
                'count': len(low_risk),
                'percentage': len(low_risk) / len(test_names) * 100,
                'tests': low_risk
            }
        }
