"""
Logging configuration for ITS
"""
import logging
import os
from datetime import datetime
from typing import Optional


class ITSLogger:
    """Custom logger for Intelligent Test Selection"""

    def __init__(
        self,
        name: str = 'ITS',
        log_file: Optional[str] = None,
        level: str = 'INFO',
        format_type: str = 'detailed'
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatters
        if format_type == 'detailed':
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter('%(levelname)s: %(message)s')

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def log_test_selection(
        self,
        total_tests: int,
        selected_tests: int,
        time_saved: float,
        changed_files: list
    ):
        """Log test selection event"""
        self.info("=" * 50)
        self.info("Test Selection Event")
        self.info(f"Changed files: {len(changed_files)}")
        for f in changed_files:
            self.info(f"  - {f}")
        self.info(f"Total tests: {total_tests}")
        self.info(f"Selected tests: {selected_tests}")
        self.info(f"Reduction: {(1 - selected_tests/total_tests)*100:.1f}%")
        self.info(f"Time saved: {time_saved:.2f}s")
        self.info("=" * 50)

    def log_model_training(self, metrics: dict):
        """Log model training event"""
        self.info("=" * 50)
        self.info("Model Training Completed")
        self.info(f"Test Accuracy: {metrics.get('test_accuracy', 0):.4f}")
        self.info(f"Test Precision: {metrics.get('test_precision', 0):.4f}")
        self.info(f"Test Recall: {metrics.get('test_recall', 0):.4f}")
        self.info(f"Test F1 Score: {metrics.get('test_f1', 0):.4f}")
        self.info("=" * 50)


def setup_logger(config: dict = None) -> ITSLogger:
    """Setup logger from config"""
    if config is None:
        config = {
            'level': 'INFO',
            'format': 'detailed',
            'log_file': 'logs/its.log'
        }

    logging_config = config.get('logging', {})

    return ITSLogger(
        name='ITS',
        log_file=logging_config.get('log_file', 'logs/its.log'),
        level=logging_config.get('level', 'INFO'),
        format_type=logging_config.get('format', 'detailed')
    )
