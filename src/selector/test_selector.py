"""
Main test selection system
"""
import os
import sys
import pandas as pd
import yaml
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.impact_analyzer import ImpactAnalyzer
from ml_engine.model_trainer import ModelTrainer
from ml_engine.predictor import TestFailurePredictor
from selector.prioritizer import TestPrioritizer, TestPriority


class IntelligentTestSelector:
    """Main intelligent test selection system"""

    def __init__(self, config_path: str = 'config.yaml', project_root: str = '.'):
        self.project_root = project_root
        self.config = self._load_config(config_path)

        # Initialize components
        self.impact_analyzer = ImpactAnalyzer(project_root)
        self.predictor = TestFailurePredictor()
        self.prioritizer = TestPrioritizer(
            min_tests=self.config['test_selection']['min_tests'],
            max_tests=self.config['test_selection']['max_tests'],
            coverage_target=self.config['test_selection']['coverage_target']
        )

        # Load historical data if available
        self.historical_data = None
        history_file = self.config['data']['history_file']
        if os.path.exists(history_file):
            self.historical_data = pd.read_csv(history_file)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default config
            return {
                'test_selection': {
                    'threshold': 0.7,
                    'min_tests': 5,
                    'max_tests': 100,
                    'coverage_target': 0.85
                },
                'ml_model': {
                    'algorithm': 'random_forest',
                    'n_estimators': 100,
                    'max_depth': 10,
                    'random_state': 42
                },
                'data': {
                    'history_file': 'data/test_history/test_results.csv',
                    'model_file': 'data/models/test_selector_model.pkl',
                    'features_file': 'data/models/feature_scaler.pkl'
                }
            }

    def train_model(self, history_file: Optional[str] = None) -> Dict:
        """Train the ML model"""
        if history_file:
            df = pd.read_csv(history_file)
        elif self.historical_data is not None:
            df = self.historical_data
        else:
            raise ValueError("No training data available")

        print(f"Training model with {len(df)} records...")

        # Create trainer
        trainer = ModelTrainer(
            algorithm=self.config['ml_model']['algorithm'],
            n_estimators=self.config['ml_model'].get('n_estimators', 100),
            max_depth=self.config['ml_model'].get('max_depth', 10),
            random_state=self.config['ml_model'].get('random_state', 42)
        )

        # Train
        metrics = trainer.train(
            df,
            test_size=self.config['ml_model'].get('test_size', 0.2)
        )

        # Save model
        model_path = self.config['data']['model_file']
        scaler_path = self.config['data']['features_file']
        trainer.save(model_path, scaler_path)

        # Update predictor
        self.predictor.load_model(model_path, scaler_path)

        return metrics

    def load_model(self):
        """Load trained model"""
        model_path = self.config['data']['model_file']
        scaler_path = self.config['data']['features_file']

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError(
                "Trained model not found. Please train the model first."
            )

        self.predictor.load_model(model_path, scaler_path)
        print("Model loaded successfully")

    def select_tests(
        self,
        changed_files: List[str] = None,
        threshold: Optional[float] = None,
        all_tests: List[str] = None
    ) -> List[str]:
        """
        Select tests to run based on code changes

        Args:
            changed_files: List of changed source files
            threshold: Probability threshold for selection
            all_tests: List of all available tests (if None, discover from history)

        Returns:
            List of selected test names
        """
        if threshold is None:
            threshold = self.config['test_selection']['threshold']

        # Load model if not already loaded
        if not self.predictor.trainer.is_trained:
            self.load_model()

        # Get all available tests
        if all_tests is None:
            if self.historical_data is None:
                raise ValueError("No historical data available")
            all_tests = self.historical_data['full_test_name'].unique().tolist()

        # If no changes specified, analyze git repo
        if changed_files is None:
            changed_files = self.impact_analyzer.diff_analyzer.get_uncommitted_changes()
            if not changed_files:
                print("No code changes detected")
                return []

        print(f"\nAnalyzing {len(changed_files)} changed files...")
        for f in changed_files:
            print(f"  - {f}")

        # Analyze impact
        impact_scores = self.impact_analyzer.analyze_change_impact(changed_files)

        print(f"\n{len(impact_scores)} test files potentially affected")

        # Get failure predictions
        print("\nPredicting test failures...")
        failure_predictions = self.predictor.predict_test_failures(
            all_tests,
            self.historical_data
        )

        # Prioritize tests
        print("Prioritizing tests...")
        priorities = self.prioritizer.prioritize_tests(
            all_tests,
            failure_predictions,
            self.historical_data,
            changed_files,
            impact_scores
        )

        # Select optimal suite
        selected_priorities = self.prioritizer.select_optimal_test_suite(priorities)

        # Get summary
        summary = self.prioritizer.get_selection_summary(priorities, selected_priorities)

        print("\n" + "="*50)
        print("TEST SELECTION SUMMARY")
        print("="*50)
        print(f"Total tests: {summary['total_tests']}")
        print(f"Selected tests: {summary['selected_tests']}")
        print(f"Reduction: {summary['reduction_percentage']:.1f}%")
        print(f"\nEstimated execution time:")
        print(f"  All tests: {summary['total_execution_time_all']:.2f}s")
        print(f"  Selected: {summary['total_execution_time_selected']:.2f}s")
        print(f"  Time saved: {summary['time_saved']:.2f}s ({summary['time_reduction_percentage']:.1f}%)")
        print("="*50 + "\n")

        # Return test names
        return [p.test_name for p in selected_priorities]

    def get_test_priorities(
        self,
        changed_files: List[str] = None,
        all_tests: List[str] = None
    ) -> List[TestPriority]:
        """
        Get prioritized list of tests with detailed information

        Returns:
            List of TestPriority objects
        """
        # Load model if not already loaded
        if not self.predictor.trainer.is_trained:
            self.load_model()

        # Get all available tests
        if all_tests is None:
            if self.historical_data is None:
                raise ValueError("No historical data available")
            all_tests = self.historical_data['full_test_name'].unique().tolist()

        # If no changes specified, analyze git repo
        if changed_files is None:
            changed_files = self.impact_analyzer.diff_analyzer.get_uncommitted_changes()

        # Analyze impact
        impact_scores = {}
        if changed_files:
            impact_scores = self.impact_analyzer.analyze_change_impact(changed_files)

        # Get failure predictions
        failure_predictions = self.predictor.predict_test_failures(
            all_tests,
            self.historical_data
        )

        # Prioritize tests
        priorities = self.prioritizer.prioritize_tests(
            all_tests,
            failure_predictions,
            self.historical_data,
            changed_files,
            impact_scores
        )

        return priorities

    def generate_test_report(
        self,
        priorities: List[TestPriority],
        output_file: str = 'test_selection_report.md'
    ):
        """Generate markdown report of test selection"""
        with open(output_file, 'w') as f:
            f.write("# Test Selection Report\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- Total tests analyzed: {len(priorities)}\n")
            f.write(f"- High priority tests: {len([p for p in priorities if p.priority_score > 0.7])}\n")
            f.write(f"- Medium priority tests: {len([p for p in priorities if 0.3 <= p.priority_score <= 0.7])}\n")
            f.write(f"- Low priority tests: {len([p for p in priorities if p.priority_score < 0.3])}\n\n")

            # Top priorities
            f.write("## Top 20 Priority Tests\n\n")
            f.write("| Rank | Test Name | Priority | Failure Prob | Reason |\n")
            f.write("|------|-----------|----------|--------------|--------|\n")

            for i, p in enumerate(priorities[:20], 1):
                f.write(f"| {i} | `{p.test_name}` | {p.priority_score:.3f} | {p.failure_probability:.3f} | {p.reason} |\n")

        print(f"\nReport generated: {output_file}")
