"""
pytest plugin for Intelligent Test Selection
"""
import pytest
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))


def pytest_addoption(parser):
    """Add command line options for ITS"""
    group = parser.getgroup('its', 'Intelligent Test Selection')

    group.addoption(
        '--its-enabled',
        action='store_true',
        default=False,
        help='Enable intelligent test selection'
    )

    group.addoption(
        '--its-threshold',
        type=float,
        default=0.7,
        help='Threshold for test selection (0.0 to 1.0)'
    )

    group.addoption(
        '--its-config',
        type=str,
        default='config.yaml',
        help='Path to ITS configuration file'
    )


def pytest_configure(config):
    """Configure pytest with ITS"""
    if config.getoption('--its-enabled'):
        # Register marker
        config.addinivalue_line(
            'markers',
            'its: Intelligent Test Selection markers'
        )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on ITS"""
    if not config.getoption('--its-enabled'):
        return

    try:
        from selector.test_selector import IntelligentTestSelector

        # Initialize selector
        its_config = config.getoption('--its-config')
        threshold = config.getoption('--its-threshold')

        selector = IntelligentTestSelector(
            config_path=its_config,
            project_root='.'
        )

        # Get selected tests
        selected_tests = selector.select_tests(threshold=threshold)

        # Filter items
        selected = []
        skipped = []

        for item in items:
            # Get test nodeid (e.g., "tests/test_auth.py::test_login")
            test_id = item.nodeid

            # Check if test should be run
            if any(test_id.endswith(selected_test.split('::')[-1]) for selected_test in selected_tests):
                selected.append(item)
            else:
                skipped.append(item)
                item.add_marker(pytest.mark.skip(reason="Skipped by ITS"))

        # Update items
        items[:] = selected

        print(f"\n\n{'='*60}")
        print("INTELLIGENT TEST SELECTION")
        print(f"{'='*60}")
        print(f"Total tests: {len(selected) + len(skipped)}")
        print(f"Selected: {len(selected)}")
        print(f"Skipped: {len(skipped)}")
        print(f"Reduction: {len(skipped)/(len(selected)+len(skipped))*100:.1f}%")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Warning: ITS failed with error: {e}")
        print("Running all tests instead...")


def pytest_report_header(config):
    """Add ITS info to pytest header"""
    if config.getoption('--its-enabled'):
        return [
            f"Intelligent Test Selection: ENABLED",
            f"Threshold: {config.getoption('--its-threshold')}"
        ]
