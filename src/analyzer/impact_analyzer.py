"""
Analyzes impact of code changes on tests
"""
import os
import sys
from typing import Dict, List, Set, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.ast_analyzer import ASTAnalyzer
from analyzer.diff_analyzer import DiffAnalyzer


class ImpactAnalyzer:
    """Analyzes the impact of code changes on tests"""

    def __init__(self, project_root: str = '.'):
        self.project_root = project_root
        self.ast_analyzer = ASTAnalyzer()
        self.diff_analyzer = DiffAnalyzer(project_root)

        # Build test-to-source mapping
        self.test_mapping = self._build_test_mapping()

    def _build_test_mapping(self) -> Dict[str, str]:
        """Build mapping from test files to source files"""
        mapping = {}

        # Simple naming convention: test_X.py -> X.py
        test_dir = os.path.join(self.project_root, 'tests', 'sample_project')
        if os.path.exists(test_dir):
            for filename in os.listdir(test_dir):
                if filename.startswith('test_') and filename.endswith('.py'):
                    test_file = os.path.join('tests', 'sample_project', filename)
                    source_file = os.path.join('tests', 'sample_project', filename.replace('test_', ''))

                    if os.path.exists(os.path.join(self.project_root, source_file)):
                        mapping[test_file] = source_file

        return mapping

    def analyze_change_impact(self, changed_files: List[str]) -> Dict[str, float]:
        """
        Analyze impact of changed files on tests
        Returns dict mapping test files to impact scores (0.0 to 1.0)
        """
        impact_scores = {}

        for test_file, source_file in self.test_mapping.items():
            impact = 0.0

            # Direct impact: source file was changed
            if source_file in changed_files:
                impact = 1.0

            # Indirect impact: imported modules were changed
            else:
                # Check if test file imports any changed modules
                test_analysis = self.ast_analyzer.analyze_file(
                    os.path.join(self.project_root, test_file)
                )

                if test_analysis:
                    for changed_file in changed_files:
                        # Check if changed file is in imports
                        module_name = self._file_to_module(changed_file)
                        if any(module_name in imp for imp in test_analysis.imports):
                            impact = max(impact, 0.5)

            if impact > 0:
                impact_scores[test_file] = impact

        return impact_scores

    def get_affected_tests(self, changed_files: List[str], threshold: float = 0.3) -> List[str]:
        """Get list of tests affected by changes"""
        impact_scores = self.analyze_change_impact(changed_files)
        return [test for test, score in impact_scores.items() if score >= threshold]

    def calculate_test_priority(
        self,
        test_file: str,
        changed_files: List[str],
        historical_failure_rate: float = 0.0,
        recent_failures: int = 0
    ) -> float:
        """
        Calculate priority score for a test
        Higher score = higher priority
        """
        priority = 0.0

        # Factor 1: Impact of code changes (weight: 0.4)
        impact_scores = self.analyze_change_impact(changed_files)
        code_impact = impact_scores.get(test_file, 0.0)
        priority += code_impact * 0.4

        # Factor 2: Historical failure rate (weight: 0.3)
        priority += historical_failure_rate * 0.3

        # Factor 3: Recent failures (weight: 0.3)
        recent_failure_score = min(recent_failures / 5.0, 1.0)  # Normalize to 0-1
        priority += recent_failure_score * 0.3

        return min(priority, 1.0)

    def get_change_summary(self, changed_files: List[str]) -> Dict:
        """Get summary of changes"""
        summary = {
            'num_files_changed': len(changed_files),
            'changed_files': changed_files,
            'total_lines_added': 0,
            'total_lines_removed': 0,
            'affected_tests': [],
            'high_priority_tests': []
        }

        # Analyze each changed file
        for file_path in changed_files:
            diff = self.diff_analyzer.analyze_diff(file_path)
            if diff:
                summary['total_lines_added'] += diff.lines_added
                summary['total_lines_removed'] += diff.lines_removed

        # Get affected tests
        impact_scores = self.analyze_change_impact(changed_files)
        summary['affected_tests'] = list(impact_scores.keys())
        summary['high_priority_tests'] = [
            test for test, score in impact_scores.items() if score >= 0.7
        ]

        return summary

    def _file_to_module(self, file_path: str) -> str:
        """Convert file path to module name"""
        # Remove .py extension and convert path separators to dots
        module = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')

        # Remove leading dots
        module = module.lstrip('.')

        return module

    def find_related_tests(self, source_file: str) -> List[str]:
        """Find tests related to a source file"""
        related_tests = []

        for test_file, mapped_source in self.test_mapping.items():
            if mapped_source == source_file:
                related_tests.append(test_file)

        return related_tests

    def estimate_test_execution_time(self, test_files: List[str], avg_times: Dict[str, float]) -> float:
        """Estimate total execution time for given tests"""
        total_time = 0.0

        for test_file in test_files:
            # Use provided average time or estimate based on file size
            if test_file in avg_times:
                total_time += avg_times[test_file]
            else:
                # Default estimate: 0.1 seconds per test
                full_path = os.path.join(self.project_root, test_file)
                if os.path.exists(full_path):
                    # Rough estimate based on file size
                    total_time += 0.1 * (os.path.getsize(full_path) / 1000)

        return total_time
