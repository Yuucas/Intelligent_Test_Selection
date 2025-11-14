"""
Feature extraction for ML model
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from sklearn.preprocessing import StandardScaler
import joblib
import os


class FeatureExtractor:
    """Extracts features from test execution history"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from test history dataframe"""
        features_df = pd.DataFrame()

        # Group by test for aggregation
        test_groups = df.groupby('full_test_name')

        # Feature 1: Historical failure rate
        features_df['historical_failure_rate'] = test_groups['passed'].transform(
            lambda x: 1 - x.mean()
        )

        # Feature 2: Recent failure count (last 10 runs)
        features_df['recent_failures'] = test_groups['passed'].transform(
            lambda x: x.tail(10).apply(lambda v: 0 if v else 1).sum()
        )

        # Feature 3: Average execution time
        features_df['avg_execution_time'] = test_groups['execution_time'].transform('mean')

        # Feature 4: Execution time variance (stability)
        features_df['execution_time_variance'] = test_groups['execution_time'].transform('std').fillna(0)

        # Feature 5: Code change frequency
        features_df['code_change_frequency'] = test_groups['lines_changed'].transform(
            lambda x: (x > 0).sum() / len(x)
        )

        # Feature 6: Lines changed (current)
        features_df['lines_changed'] = df['lines_changed']

        # Feature 7: Functions changed (current)
        features_df['functions_changed'] = df['functions_changed']

        # Feature 8: Test coupling (fails when source changes)
        features_df['test_coupling'] = df.apply(
            lambda row: 1.0 if row['lines_changed'] > 0 and not row['passed'] else 0.0,
            axis=1
        )

        # Feature 9: Is flaky test
        features_df['is_flaky'] = df['is_flaky'].astype(int)

        # Feature 10: Test age (runs since first appearance)
        features_df['test_age'] = test_groups['run_id'].transform(
            lambda x: x - x.min()
        )

        # Feature 11: Coverage
        features_df['coverage'] = df['coverage']

        # Feature 12: Failure streak (consecutive recent failures)
        def calculate_failure_streak(group):
            streak = 0
            for passed in group['passed'].tail(10)[::-1]:
                if not passed:
                    streak += 1
                else:
                    break
            return streak

        features_df['failure_streak'] = test_groups.apply(calculate_failure_streak)
        features_df['failure_streak'] = features_df['failure_streak'].fillna(0)

        # Feature 13: Time since last failure
        def time_since_last_failure(group):
            failures = group[group['passed'] == False]
            if len(failures) == 0:
                return 999  # Large number if never failed
            return len(group) - failures.index[-1] - 1

        features_df['time_since_last_failure'] = test_groups.apply(time_since_last_failure)
        features_df['time_since_last_failure'] = features_df['time_since_last_failure'].fillna(999)

        self.feature_names = features_df.columns.tolist()

        return features_df

    def extract_features_for_prediction(
        self,
        test_name: str,
        historical_data: pd.DataFrame,
        lines_changed: int = 0,
        functions_changed: int = 0
    ) -> np.ndarray:
        """
        Extract features for a single test prediction
        """
        # Get historical data for this test
        test_history = historical_data[historical_data['full_test_name'] == test_name]

        if len(test_history) == 0:
            # New test with no history - return default features
            return self._get_default_features(lines_changed, functions_changed)

        # Calculate features
        features = {}

        # Historical failure rate
        features['historical_failure_rate'] = 1 - test_history['passed'].mean()

        # Recent failures (last 10 runs)
        features['recent_failures'] = test_history['passed'].tail(10).apply(lambda x: 0 if x else 1).sum()

        # Average execution time
        features['avg_execution_time'] = test_history['execution_time'].mean()

        # Execution time variance
        features['execution_time_variance'] = test_history['execution_time'].std() if len(test_history) > 1 else 0

        # Code change frequency
        features['code_change_frequency'] = (test_history['lines_changed'] > 0).sum() / len(test_history)

        # Current changes
        features['lines_changed'] = lines_changed
        features['functions_changed'] = functions_changed

        # Test coupling
        coupling_cases = test_history[(test_history['lines_changed'] > 0) & (test_history['passed'] == False)]
        features['test_coupling'] = len(coupling_cases) / len(test_history) if len(test_history) > 0 else 0

        # Is flaky
        features['is_flaky'] = test_history['is_flaky'].iloc[-1] if 'is_flaky' in test_history.columns else 0

        # Test age
        features['test_age'] = len(test_history)

        # Coverage
        features['coverage'] = test_history['coverage'].mean()

        # Failure streak
        streak = 0
        for passed in test_history['passed'].tail(10)[::-1]:
            if not passed:
                streak += 1
            else:
                break
        features['failure_streak'] = streak

        # Time since last failure
        failures = test_history[test_history['passed'] == False]
        if len(failures) == 0:
            features['time_since_last_failure'] = 999
        else:
            features['time_since_last_failure'] = len(test_history) - failures.index[-1] - 1

        # Convert to array in correct order
        feature_array = np.array([features[name] for name in self.feature_names])

        return feature_array.reshape(1, -1)

    def _get_default_features(self, lines_changed: int, functions_changed: int) -> np.ndarray:
        """Get default features for a test with no history"""
        features = {
            'historical_failure_rate': 0.05,  # Assume 5% base failure rate
            'recent_failures': 0,
            'avg_execution_time': 0.1,
            'execution_time_variance': 0.0,
            'code_change_frequency': 0.0,
            'lines_changed': lines_changed,
            'functions_changed': functions_changed,
            'test_coupling': 0.0,
            'is_flaky': 0,
            'test_age': 0,
            'coverage': 0.8,
            'failure_streak': 0,
            'time_since_last_failure': 999
        }

        # Ensure we have all feature names
        if not self.feature_names:
            self.feature_names = list(features.keys())

        feature_array = np.array([features[name] for name in self.feature_names])
        return feature_array.reshape(1, -1)

    def fit_scaler(self, features_df: pd.DataFrame):
        """Fit the feature scaler"""
        self.scaler.fit(features_df)

    def transform(self, features_df: pd.DataFrame) -> np.ndarray:
        """Transform features using fitted scaler"""
        return self.scaler.transform(features_df)

    def fit_transform(self, features_df: pd.DataFrame) -> np.ndarray:
        """Fit scaler and transform features"""
        return self.scaler.fit_transform(features_df)

    def save(self, filepath: str):
        """Save feature extractor"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, filepath)

    def load(self, filepath: str):
        """Load feature extractor"""
        data = joblib.load(filepath)
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
