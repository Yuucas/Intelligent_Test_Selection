"""
Generate synthetic test execution history for training
"""
import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import json


class TestHistoryGenerator:
    """Generates synthetic test execution history"""

    def __init__(self, output_dir: str = 'data/test_history'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Define test modules and files
        self.test_files = [
            'tests/sample_project/test_auth.py',
            'tests/sample_project/test_database.py',
            'tests/sample_project/test_api.py',
            'tests/sample_project/test_utils.py'
        ]

        self.source_files = [
            'tests/sample_project/auth.py',
            'tests/sample_project/database.py',
            'tests/sample_project/api.py',
            'tests/sample_project/utils.py'
        ]

        # Test to source file mapping
        self.test_to_source = {
            'tests/sample_project/test_auth.py': 'tests/sample_project/auth.py',
            'tests/sample_project/test_database.py': 'tests/sample_project/database.py',
            'tests/sample_project/test_api.py': 'tests/sample_project/api.py',
            'tests/sample_project/test_utils.py': 'tests/sample_project/utils.py'
        }

        # Test names per file
        self.test_cases = {
            'tests/sample_project/test_auth.py': [
                'test_register_user_success',
                'test_register_user_duplicate_username',
                'test_register_user_invalid_email',
                'test_register_user_weak_password',
                'test_login_success',
                'test_login_invalid_username',
                'test_login_wrong_password',
                'test_login_attempts_lockout',
                'test_logout_success',
                'test_validate_session_valid',
                'test_reset_password_success'
            ],
            'tests/sample_project/test_database.py': [
                'test_create_table_success',
                'test_create_table_duplicate',
                'test_insert_record',
                'test_find_by_id_success',
                'test_find_all',
                'test_update_record',
                'test_delete_record',
                'test_query_with_filter',
                'test_count',
                'test_export_to_json',
                'test_import_from_json'
            ],
            'tests/sample_project/test_api.py': [
                'test_client_initialization',
                'test_set_auth_token',
                'test_get_request',
                'test_post_request',
                'test_put_request',
                'test_delete_request',
                'test_limiter_initialization',
                'test_can_make_request_under_limit',
                'test_api_error_initialization'
            ],
            'tests/sample_project/test_utils.py': [
                'test_valid_email',
                'test_sanitize_clean_string',
                'test_calculate_percentage_normal',
                'test_format_usd',
                'test_chunk_list_even',
                'test_flatten_nested_dict',
                'test_merge_two_dicts',
                'test_remove_duplicates_with_dupes',
                'test_is_palindrome_true',
                'test_truncate_long_string',
                'test_parse_query_string',
                'test_to_snake_case'
            ]
        }

    def generate_history(self, num_runs: int = 100) -> pd.DataFrame:
        """Generate synthetic test execution history"""
        print(f"Generating {num_runs} test execution runs...")

        records = []
        start_date = datetime.now() - timedelta(days=90)

        # Track test failure patterns
        flaky_tests = self._select_flaky_tests()
        stable_tests = [
            test for test_file in self.test_cases
            for test in self.test_cases[test_file]
            if test not in flaky_tests
        ]

        for run_id in range(1, num_runs + 1):
            run_date = start_date + timedelta(days=run_id * 0.9)

            # Randomly select which files were changed
            num_changed_files = random.randint(1, 3)
            changed_files = random.sample(self.source_files, num_changed_files)

            # Determine which tests to run (all in this case for history)
            for test_file in self.test_files:
                source_file = self.test_to_source[test_file]

                for test_name in self.test_cases[test_file]:
                    full_test_name = f"{test_file}::{test_name}"

                    # Calculate failure probability
                    failure_prob = self._calculate_failure_probability(
                        test_name, source_file, changed_files, flaky_tests
                    )

                    # Determine if test passed or failed
                    passed = random.random() > failure_prob

                    # Generate execution time
                    base_time = random.uniform(0.01, 0.5)
                    execution_time = base_time if passed else base_time * random.uniform(1.2, 2.0)

                    # Code coverage (simplified)
                    coverage = random.uniform(0.7, 0.95)

                    # Code change metrics
                    lines_changed = 0
                    functions_changed = 0
                    if source_file in changed_files:
                        lines_changed = random.randint(5, 100)
                        functions_changed = random.randint(1, 10)

                    record = {
                        'run_id': run_id,
                        'timestamp': run_date.isoformat(),
                        'test_file': test_file,
                        'test_name': test_name,
                        'full_test_name': full_test_name,
                        'source_file': source_file,
                        'passed': passed,
                        'execution_time': round(execution_time, 3),
                        'coverage': round(coverage, 3),
                        'lines_changed': lines_changed,
                        'functions_changed': functions_changed,
                        'files_changed': ','.join(changed_files),
                        'is_flaky': test_name in flaky_tests
                    }

                    records.append(record)

            if run_id % 10 == 0:
                print(f"  Generated {run_id}/{num_runs} runs...")

        df = pd.DataFrame(records)

        # Add calculated features
        df = self._add_calculated_features(df)

        # Save to CSV
        output_file = os.path.join(self.output_dir, 'test_results.csv')
        df.to_csv(output_file, index=False)
        print(f"\nSaved test history to: {output_file}")
        print(f"Total records: {len(df)}")
        print(f"Pass rate: {(df['passed'].sum() / len(df) * 100):.2f}%")

        # Save metadata
        self._save_metadata(df, num_runs)

        return df

    def _select_flaky_tests(self) -> List[str]:
        """Select some tests to be flaky"""
        all_tests = [
            test for test_file in self.test_cases
            for test in self.test_cases[test_file]
        ]
        num_flaky = max(1, len(all_tests) // 10)  # 10% flaky
        return random.sample(all_tests, num_flaky)

    def _calculate_failure_probability(
        self,
        test_name: str,
        source_file: str,
        changed_files: List[str],
        flaky_tests: List[str]
    ) -> float:
        """Calculate probability of test failure"""
        base_prob = 0.05  # Base 5% failure rate

        # Increase probability if source file was changed
        if source_file in changed_files:
            base_prob += 0.15

        # Flaky tests have higher failure rate
        if test_name in flaky_tests:
            base_prob += 0.20

        # Add some randomness
        base_prob += random.uniform(-0.02, 0.02)

        return max(0, min(1, base_prob))

    def _add_calculated_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated features for ML"""
        # Historical failure rate per test
        df['historical_failure_rate'] = df.groupby('full_test_name')['passed'].transform(
            lambda x: 1 - x.mean()
        )

        # Recent failure count (last 10 runs)
        def recent_failures(group):
            return group.tail(10)['passed'].apply(lambda x: 0 if x else 1).sum()

        df['recent_failures'] = df.groupby('full_test_name')['passed'].transform(
            lambda group: group.rolling(10, min_periods=1).apply(lambda x: (x == 0).sum())
        )

        # Average execution time per test
        df['avg_execution_time'] = df.groupby('full_test_name')['execution_time'].transform('mean')

        # Test coupling (how often it fails when source changes)
        df['test_coupling'] = df.apply(
            lambda row: 1.0 if row['source_file'] in row['files_changed'] else 0.0,
            axis=1
        )

        return df

    def _save_metadata(self, df: pd.DataFrame, num_runs: int):
        """Save metadata about generated data"""
        metadata = {
            'generation_date': datetime.now().isoformat(),
            'num_runs': num_runs,
            'num_tests': df['full_test_name'].nunique(),
            'num_test_files': len(self.test_files),
            'num_source_files': len(self.source_files),
            'total_records': len(df),
            'overall_pass_rate': float(df['passed'].mean()),
            'test_files': self.test_files,
            'source_files': self.source_files
        }

        metadata_file = os.path.join(self.output_dir, 'metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Saved metadata to: {metadata_file}")


def generate_sample_data(num_runs: int = 100):
    """Generate sample test execution history"""
    generator = TestHistoryGenerator()
    df = generator.generate_history(num_runs)
    return df


if __name__ == '__main__':
    import sys

    num_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_sample_data(num_runs)
