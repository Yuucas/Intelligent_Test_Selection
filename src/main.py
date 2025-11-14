"""
Main entry point for Intelligent Test Selection system
"""
import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selector.test_selector import IntelligentTestSelector
from data_generator import generate_sample_data
from logger import setup_logger


def main():
    parser = argparse.ArgumentParser(
        description='Intelligent Test Selection System'
    )

    parser.add_argument(
        '--mode',
        choices=['generate-history', 'train', 'select', 'report'],
        required=True,
        help='Operation mode'
    )

    parser.add_argument(
        '--num-runs',
        type=int,
        default=100,
        help='Number of test runs to generate (for generate-history mode)'
    )

    parser.add_argument(
        '--history-file',
        type=str,
        default='data/test_history/test_results.csv',
        help='Path to test history file'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.7,
        help='Selection threshold for test selection'
    )

    parser.add_argument(
        '--changed-files',
        nargs='*',
        help='List of changed files (optional, will auto-detect if not provided)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='test_selection_report.md',
        help='Output file for reports'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    # Setup logger
    logger = setup_logger()

    if args.mode == 'generate-history':
        logger.info(f"Generating {args.num_runs} test execution runs...")
        df = generate_sample_data(args.num_runs)
        logger.info(f"Generated {len(df)} test records")
        logger.info(f"Saved to: {args.history_file}")

    elif args.mode == 'train':
        logger.info("Training ML model...")
        selector = IntelligentTestSelector(
            config_path=args.config,
            project_root='.'
        )

        metrics = selector.train_model(args.history_file)
        logger.log_model_training(metrics)

        # Print feature importance
        if 'feature_importance' in metrics:
            logger.info("\nTop 10 Feature Importances:")
            for i, (feature, importance) in enumerate(
                list(metrics['feature_importance'].items())[:10], 1
            ):
                logger.info(f"  {i}. {feature}: {importance:.4f}")

    elif args.mode == 'select':
        logger.info("Selecting tests based on code changes...")
        selector = IntelligentTestSelector(
            config_path=args.config,
            project_root='.'
        )

        # Select tests
        selected_tests = selector.select_tests(
            changed_files=args.changed_files,
            threshold=args.threshold
        )

        logger.info(f"\nSelected {len(selected_tests)} tests to run:")
        for i, test in enumerate(selected_tests[:20], 1):
            logger.info(f"  {i}. {test}")

        if len(selected_tests) > 20:
            logger.info(f"  ... and {len(selected_tests) - 20} more tests")

        # Save to file
        output_file = 'selected_tests.txt'
        with open(output_file, 'w') as f:
            for test in selected_tests:
                f.write(f"{test}\n")
        logger.info(f"\nSelected tests saved to: {output_file}")

    elif args.mode == 'report':
        logger.info("Generating test selection report...")
        selector = IntelligentTestSelector(
            config_path=args.config,
            project_root='.'
        )

        priorities = selector.get_test_priorities(
            changed_files=args.changed_files
        )

        selector.generate_test_report(priorities, args.output)
        logger.info(f"Report saved to: {args.output}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
