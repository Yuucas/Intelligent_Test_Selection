"""
Test prioritization logic
"""
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TestPriority:
    """Represents a prioritized test"""
    test_name: str
    priority_score: float
    failure_probability: float
    execution_time: float
    recent_failures: int
    lines_changed: int
    reason: str


class TestPrioritizer:
    """Prioritizes tests based on multiple factors"""

    def __init__(
        self,
        min_tests: int = 5,
        max_tests: int = 100,
        coverage_target: float = 0.85
    ):
        self.min_tests = min_tests
        self.max_tests = max_tests
        self.coverage_target = coverage_target

    def prioritize_tests(
        self,
        test_names: List[str],
        failure_probabilities: Dict[str, float],
        historical_data: pd.DataFrame,
        changed_files: List[str] = None,
        impact_scores: Dict[str, float] = None
    ) -> List[TestPriority]:
        """
        Prioritize tests based on multiple factors

        Factors considered:
        1. ML-predicted failure probability (40%)
        2. Code change impact (30%)
        3. Historical failure rate (15%)
        4. Recent failures (15%)
        """
        if changed_files is None:
            changed_files = []

        if impact_scores is None:
            impact_scores = {}

        priorities = []

        for test_name in test_names:
            # Get test history
            test_history = historical_data[
                historical_data['full_test_name'] == test_name
            ]

            if len(test_history) == 0:
                # New test - give it medium priority
                priority = self._calculate_new_test_priority(
                    test_name, failure_probabilities.get(test_name, 0.5)
                )
                priorities.append(priority)
                continue

            # Factor 1: ML prediction (40%)
            failure_prob = failure_probabilities.get(test_name, 0.0)
            ml_score = failure_prob * 0.4

            # Factor 2: Code change impact (30%)
            test_file = test_name.split('::')[0] if '::' in test_name else ''
            impact = impact_scores.get(test_file, 0.0)
            impact_score = impact * 0.3

            # Factor 3: Historical failure rate (15%)
            historical_failure_rate = 1 - test_history['passed'].mean()
            historical_score = historical_failure_rate * 0.15

            # Factor 4: Recent failures (15%)
            recent_failures = test_history['passed'].tail(10).apply(lambda x: 0 if x else 1).sum()
            recent_score = min(recent_failures / 5.0, 1.0) * 0.15

            # Total priority score
            priority_score = ml_score + impact_score + historical_score + recent_score

            # Get additional metrics
            avg_execution_time = test_history['execution_time'].mean()
            lines_changed = test_history['lines_changed'].iloc[-1] if len(test_history) > 0 else 0

            # Determine reason for priority
            reason = self._determine_priority_reason(
                failure_prob, impact, historical_failure_rate, recent_failures
            )

            priority = TestPriority(
                test_name=test_name,
                priority_score=priority_score,
                failure_probability=failure_prob,
                execution_time=avg_execution_time,
                recent_failures=recent_failures,
                lines_changed=lines_changed,
                reason=reason
            )

            priorities.append(priority)

        # Sort by priority score (highest first)
        priorities.sort(key=lambda x: x.priority_score, reverse=True)

        return priorities

    def select_optimal_test_suite(
        self,
        priorities: List[TestPriority],
        time_budget: Optional[float] = None
    ) -> List[TestPriority]:
        """
        Select optimal test suite based on priorities and constraints

        Args:
            priorities: List of prioritized tests
            time_budget: Optional time budget in seconds

        Returns:
            Selected subset of tests
        """
        selected = []
        total_time = 0.0

        # Always include minimum number of tests
        for i, priority in enumerate(priorities):
            if i < self.min_tests:
                selected.append(priority)
                total_time += priority.execution_time
                continue

            # Check constraints
            if len(selected) >= self.max_tests:
                break

            if time_budget and total_time + priority.execution_time > time_budget:
                break

            # Include if priority score is significant
            if priority.priority_score >= 0.3:  # Threshold
                selected.append(priority)
                total_time += priority.execution_time

        return selected

    def _calculate_new_test_priority(
        self,
        test_name: str,
        failure_probability: float
    ) -> TestPriority:
        """Calculate priority for a test with no history"""
        return TestPriority(
            test_name=test_name,
            priority_score=0.5,  # Medium priority
            failure_probability=failure_probability,
            execution_time=0.1,  # Estimated
            recent_failures=0,
            lines_changed=0,
            reason="New test"
        )

    def _determine_priority_reason(
        self,
        failure_prob: float,
        impact: float,
        historical_rate: float,
        recent_failures: int
    ) -> str:
        """Determine the main reason for test priority"""
        scores = {
            'High failure risk': failure_prob,
            'Code changes': impact,
            'Historical failures': historical_rate,
            'Recent failures': min(recent_failures / 5.0, 1.0)
        }

        # Get highest scoring factor
        main_reason = max(scores.items(), key=lambda x: x[1])

        if main_reason[1] > 0.5:
            return main_reason[0]
        else:
            return "General testing"

    def get_selection_summary(
        self,
        all_tests: List[TestPriority],
        selected_tests: List[TestPriority]
    ) -> Dict:
        """Get summary of test selection"""
        total_time_all = sum(t.execution_time for t in all_tests)
        total_time_selected = sum(t.execution_time for t in selected_tests)

        time_saved = total_time_all - total_time_selected
        time_reduction_pct = (time_saved / total_time_all * 100) if total_time_all > 0 else 0

        return {
            'total_tests': len(all_tests),
            'selected_tests': len(selected_tests),
            'reduction_percentage': (1 - len(selected_tests) / len(all_tests)) * 100,
            'total_execution_time_all': total_time_all,
            'total_execution_time_selected': total_time_selected,
            'time_saved': time_saved,
            'time_reduction_percentage': time_reduction_pct,
            'high_priority_count': len([t for t in selected_tests if t.priority_score > 0.7]),
            'medium_priority_count': len([t for t in selected_tests if 0.3 <= t.priority_score <= 0.7]),
            'low_priority_count': len([t for t in selected_tests if t.priority_score < 0.3])
        }
