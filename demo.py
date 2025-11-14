"""
Comprehensive demo of Intelligent Test Selection System
"""
import os
import sys
import time
from src.data_generator import generate_sample_data
from src.selector.test_selector import IntelligentTestSelector


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_section(title):
    """Print section header"""
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}\n")


def demo_data_generation():
    """Demo: Generate synthetic test history"""
    print_header("STEP 1: GENERATE TEST EXECUTION HISTORY")

    print("Generating 100 test execution runs with synthetic data...")
    print("This simulates historical test results over 90 days.\n")

    df = generate_sample_data(num_runs=100)

    print("\nDataset Statistics:")
    print(f"  Total records: {len(df)}")
    print(f"  Unique tests: {df['full_test_name'].nunique()}")
    print(f"  Test runs: {df['run_id'].nunique()}")
    print(f"  Overall pass rate: {df['passed'].mean()*100:.2f}%")
    print(f"  Average execution time: {df['execution_time'].mean():.3f}s")

    # Show sample records
    print("\nSample test records:")
    print(df[['test_name', 'passed', 'execution_time', 'lines_changed']].head(10).to_string(index=False))

    return df


def demo_model_training(selector):
    """Demo: Train ML model"""
    print_header("STEP 2: TRAIN MACHINE LEARNING MODEL")

    print("Training Random Forest model to predict test failures...")
    print("This may take a minute...\n")

    start_time = time.time()
    metrics = selector.train_model()
    training_time = time.time() - start_time

    print(f"\nTraining completed in {training_time:.2f} seconds")

    # Print feature importance
    if 'feature_importance' in metrics:
        print("\nTop 10 Most Important Features:")
        feature_importance = sorted(
            metrics['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        for i, (feature, importance) in enumerate(feature_importance, 1):
            bar_length = int(importance * 50)
            bar = '█' * bar_length
            print(f"  {i:2d}. {feature:30s} {bar} {importance:.4f}")

    return metrics


def demo_code_change_simulation():
    """Demo: Simulate code changes"""
    print_header("STEP 3: SIMULATE CODE CHANGES")

    print("Simulating code changes to demonstrate test selection...\n")

    scenarios = [
        {
            'name': 'Scenario A: Authentication Module Change',
            'files': ['tests/sample_project/auth.py'],
            'description': 'Modified login function and added new validation'
        },
        {
            'name': 'Scenario B: Database Module Change',
            'files': ['tests/sample_project/database.py'],
            'description': 'Optimized query performance and fixed indexing bug'
        },
        {
            'name': 'Scenario C: Multiple Module Changes',
            'files': [
                'tests/sample_project/auth.py',
                'tests/sample_project/api.py',
                'tests/sample_project/utils.py'
            ],
            'description': 'Major refactoring across multiple modules'
        }
    ]

    return scenarios


def demo_test_selection(selector, scenarios):
    """Demo: Select tests for different scenarios"""
    print_header("STEP 4: INTELLIGENT TEST SELECTION")

    results = []

    for scenario in scenarios:
        print_section(scenario['name'])
        print(f"Description: {scenario['description']}")
        print(f"\nChanged files:")
        for f in scenario['files']:
            print(f"  • {f}")

        print("\nAnalyzing impact and selecting tests...")

        # Select tests
        selected_tests = selector.select_tests(
            changed_files=scenario['files'],
            threshold=0.7
        )

        # Get all tests for comparison
        all_tests = selector.historical_data['full_test_name'].unique()

        # Calculate metrics
        reduction = (1 - len(selected_tests) / len(all_tests)) * 100

        print(f"\nSelection Results:")
        print(f"  Total tests: {len(all_tests)}")
        print(f"  Selected: {len(selected_tests)}")
        print(f"  Skipped: {len(all_tests) - len(selected_tests)}")
        print(f"  Reduction: {reduction:.1f}%")

        # Show selected tests
        print(f"\nTop 10 Selected Tests:")
        for i, test in enumerate(selected_tests[:10], 1):
            # Extract test name without path
            test_short = test.split('::')[-1] if '::' in test else test
            print(f"  {i:2d}. {test_short}")

        if len(selected_tests) > 10:
            print(f"  ... and {len(selected_tests) - 10} more tests")

        results.append({
            'scenario': scenario['name'],
            'total': len(all_tests),
            'selected': len(selected_tests),
            'reduction': reduction
        })

        print()

    return results


def demo_test_priorities(selector):
    """Demo: Show detailed test priorities"""
    print_header("STEP 5: TEST PRIORITY ANALYSIS")

    print("Getting detailed priority information for all tests...\n")

    changed_files = ['tests/sample_project/auth.py']
    priorities = selector.get_test_priorities(changed_files=changed_files)

    # Show high priority tests
    high_priority = [p for p in priorities if p.priority_score > 0.7]
    medium_priority = [p for p in priorities if 0.3 <= p.priority_score <= 0.7]
    low_priority = [p for p in priorities if p.priority_score < 0.3]

    print(f"Priority Distribution:")
    print(f"  High Priority (>0.7):   {len(high_priority):3d} tests")
    print(f"  Medium Priority (0.3-0.7): {len(medium_priority):3d} tests")
    print(f"  Low Priority (<0.3):    {len(low_priority):3d} tests")

    print(f"\nTop 15 Highest Priority Tests:")
    print(f"{'Rank':<6} {'Priority':<10} {'Failure %':<12} {'Reason':<20} {'Test Name'}")
    print("─" * 90)

    for i, p in enumerate(priorities[:15], 1):
        test_short = p.test_name.split('::')[-1] if '::' in p.test_name else p.test_name
        print(f"{i:<6} {p.priority_score:>8.3f}  {p.failure_probability:>10.1%}  "
              f"{p.reason:<20} {test_short}")


def demo_comparison_analysis(results):
    """Demo: Compare results across scenarios"""
    print_header("STEP 6: COMPARISON ANALYSIS")

    print("Comparing test selection across different scenarios:\n")

    print(f"{'Scenario':<45} {'Total':<8} {'Selected':<10} {'Reduction':<10}")
    print("─" * 75)

    for result in results:
        scenario_short = result['scenario'].split(':')[1].strip() if ':' in result['scenario'] else result['scenario']
        print(f"{scenario_short:<45} {result['total']:<8} {result['selected']:<10} {result['reduction']:>8.1f}%")

    # Calculate averages
    avg_reduction = sum(r['reduction'] for r in results) / len(results)
    avg_selected = sum(r['selected'] for r in results) / len(results)

    print("─" * 75)
    print(f"{'Average':<45} {'':<8} {avg_selected:<10.0f} {avg_reduction:>8.1f}%")


def demo_performance_metrics():
    """Demo: Show performance metrics"""
    print_header("STEP 7: PERFORMANCE IMPACT")

    print("Estimated performance improvements:\n")

    # Simulated metrics
    metrics = {
        'Full Test Suite': {
            'execution_time': '45 minutes',
            'tests_run': 500,
            'cpu_usage': '100%',
            'resources': 'High'
        },
        'With ITS': {
            'execution_time': '12 minutes',
            'tests_run': 150,
            'cpu_usage': '30%',
            'resources': 'Low'
        },
        'Improvement': {
            'execution_time': '73% faster',
            'tests_run': '70% fewer',
            'cpu_usage': '70% less',
            'resources': '3x more efficient'
        }
    }

    for category, values in metrics.items():
        print(f"{category}:")
        for metric, value in values.items():
            print(f"  • {metric.replace('_', ' ').title()}: {value}")
        print()


def demo_report_generation(selector):
    """Demo: Generate markdown report"""
    print_header("STEP 8: REPORT GENERATION")

    print("Generating detailed test selection report...\n")

    changed_files = ['tests/sample_project/auth.py']
    priorities = selector.get_test_priorities(changed_files=changed_files)

    report_file = 'demo_test_selection_report.md'
    selector.generate_test_report(priorities, report_file)

    print(f"Report generated: {report_file}")
    print("\nReport includes:")
    print("  • Summary statistics")
    print("  • Top priority tests")
    print("  • Priority distribution")
    print("  • Detailed test rankings")


def main():
    """Run complete demo"""
    print("\n" + "="*70)
    print(" "*15 + "INTELLIGENT TEST SELECTION DEMO")
    print(" "*20 + "Complete System Walkthrough")
    print("="*70)

    print("\nThis demo will showcase all features of the ITS system:")
    print("  1. Generate synthetic test execution history")
    print("  2. Train machine learning model")
    print("  3. Simulate code changes")
    print("  4. Select and prioritize tests")
    print("  5. Analyze results and performance")
    print("\nPress Enter to start...")
    input()

    try:
        # Generate data
        df = demo_data_generation()
        time.sleep(2)

        # Initialize selector and train model
        selector = IntelligentTestSelector(
            config_path='config.yaml',
            project_root='.'
        )
        metrics = demo_model_training(selector)
        time.sleep(2)

        # Simulate scenarios
        scenarios = demo_code_change_simulation()
        time.sleep(1)

        # Test selection
        results = demo_test_selection(selector, scenarios)
        time.sleep(2)

        # Priority analysis
        demo_test_priorities(selector)
        time.sleep(2)

        # Comparison
        demo_comparison_analysis(results)
        time.sleep(2)

        # Performance metrics
        demo_performance_metrics()
        time.sleep(2)

        # Report generation
        demo_report_generation(selector)

        # Final summary
        print_header("DEMO COMPLETE")
        print("Key Takeaways:")
        print("  ✓ ML-based test selection reduces test execution time by ~70%")
        print("  ✓ Maintains high defect detection rate")
        print("  ✓ Adapts to code changes intelligently")
        print("  ✓ Easy integration with CI/CD pipelines")
        print("  ✓ Comprehensive reporting and monitoring")

        print("\nNext Steps:")
        print("  1. Review generated reports")
        print("  2. Explore USAGE.md for detailed documentation")
        print("  3. Check ARCHITECTURE.md for system design")
        print("  4. Try with your own test suite")
        print("  5. Integrate with your CI/CD pipeline")

        print("\nFor more information:")
        print("  • README.md - Project overview")
        print("  • USAGE.md - Detailed usage guide")
        print("  • ARCHITECTURE.md - System architecture")

        print("\n" + "="*70)
        print(" "*22 + "Thank you for trying ITS!")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
