# Intelligent Test Selection - Architecture

## Overview

The Intelligent Test Selection (ITS) system uses machine learning to predict which tests are most likely to fail based on code changes, reducing test execution time while maintaining high defect detection rates.

## System Components

### 1. Code Analyzer (`src/analyzer/`)

Analyzes code changes to understand their impact on tests.

#### AST Analyzer (`ast_analyzer.py`)
- Parses Python code using Abstract Syntax Trees
- Extracts functions, classes, imports
- Calculates code complexity metrics
- Compares code versions to detect changes

#### Diff Analyzer (`diff_analyzer.py`)
- Integrates with Git to detect changes
- Analyzes diffs between commits
- Calculates change magnitude
- Identifies affected line numbers

#### Impact Analyzer (`impact_analyzer.py`)
- Maps code changes to test files
- Calculates impact scores
- Determines test-to-source relationships
- Prioritizes tests based on change impact

### 2. ML Engine (`src/ml_engine/`)

Machine learning components for test failure prediction.

#### Feature Extractor (`feature_extractor.py`)
Extracts 13 features from test execution history:

1. **Historical failure rate**: Long-term failure percentage
2. **Recent failures**: Failures in last 10 runs
3. **Average execution time**: Mean test duration
4. **Execution time variance**: Test stability measure
5. **Code change frequency**: How often related code changes
6. **Lines changed**: Current change magnitude
7. **Functions changed**: Number of modified functions
8. **Test coupling**: Correlation with source changes
9. **Is flaky**: Binary flakiness indicator
10. **Test age**: Number of runs since creation
11. **Coverage**: Code coverage percentage
12. **Failure streak**: Consecutive recent failures
13. **Time since last failure**: Runs since last failure

#### Model Trainer (`model_trainer.py`)
- Trains ML models (Random Forest, Gradient Boosting, Logistic Regression)
- Performs cross-validation
- Evaluates model performance
- Saves/loads trained models

#### Predictor (`predictor.py`)
- Predicts test failure probabilities
- Ranks tests by failure risk
- Categorizes tests into risk levels (high/medium/low)

### 3. Test Selector (`src/selector/`)

Selects and prioritizes tests for execution.

#### Prioritizer (`prioritizer.py`)
Calculates test priority scores using weighted factors:
- ML prediction (40%)
- Code change impact (30%)
- Historical failure rate (15%)
- Recent failures (15%)

Applies constraints:
- Minimum tests to run
- Maximum tests to run
- Time budget
- Coverage target

#### Test Selector (`test_selector.py`)
Main orchestrator that:
- Coordinates all components
- Loads configuration
- Manages historical data
- Selects optimal test suite
- Generates reports

### 4. Data Layer

#### Test History (`data/test_history/`)
Stores execution history:
- Test results (pass/fail)
- Execution times
- Code changes
- Coverage metrics

#### Models (`data/models/`)
Persisted ML models:
- Trained classifiers
- Feature scalers
- Model metadata

## Data Flow

```
1. Code Change Detection
   Git Diff → Changed Files → AST Analysis → Impact Scores

2. Feature Extraction
   Test History + Code Changes → Feature Vectors

3. ML Prediction
   Feature Vectors → Trained Model → Failure Probabilities

4. Test Prioritization
   Failure Probabilities + Impact + History → Priority Scores

5. Test Selection
   Priority Scores + Constraints → Selected Tests

6. Execution
   Selected Tests → pytest → Updated History
```

## Algorithms

### Test Priority Calculation

```
priority_score = (
    ml_prediction * 0.40 +
    code_impact * 0.30 +
    historical_failure_rate * 0.15 +
    recent_failures_normalized * 0.15
)
```

### Test Selection Strategy

1. **Always include**: Tests with priority > 0.7 (high risk)
2. **Consider**: Tests with priority 0.3-0.7 (medium risk)
3. **Skip**: Tests with priority < 0.3 (low risk)
4. **Constraints**: Respect min_tests, max_tests, time_budget

### Feature Engineering

Features are normalized using StandardScaler and include both:
- **Static features**: Test characteristics (age, historical rate)
- **Dynamic features**: Current context (lines changed, recent failures)

## ML Model Selection

### Random Forest (Default)
- **Pros**: Handles non-linear relationships, feature importance
- **Cons**: Can overfit, slower inference
- **Use case**: Default choice, good balance

### Gradient Boosting
- **Pros**: High accuracy, handles missing data
- **Cons**: Longer training time, hyperparameter sensitive
- **Use case**: When accuracy is critical

### Logistic Regression
- **Pros**: Fast, interpretable, simple
- **Cons**: Assumes linear relationships
- **Use case**: When speed and simplicity are priorities

## Integration Points

### pytest Integration
- Custom pytest plugin (`conftest.py`)
- Command-line options: `--its-enabled`, `--its-threshold`
- Hooks into test collection phase
- Filters tests before execution

### CI/CD Integration
- GitHub Actions workflow
- GitLab CI pipeline
- Jenkins pipeline
- Generates artifacts and reports

## Performance Characteristics

### Time Complexity
- Feature extraction: O(n) where n = number of test records
- ML prediction: O(m * log(trees)) where m = number of tests
- Test selection: O(m * log(m)) for sorting

### Space Complexity
- Model size: ~10-50 MB
- Feature cache: O(features * tests)
- History storage: ~1 KB per test run

## Configuration

All configurable via `config.yaml`:
- Selection thresholds
- ML hyperparameters
- File paths
- Logging settings

## Extensibility

### Adding New Features
1. Modify `feature_extractor.py`
2. Update feature list
3. Retrain model

### Supporting New Languages
1. Implement language-specific AST parser
2. Adapt test discovery
3. Update mapping logic

### Custom ML Models
1. Implement in `model_trainer.py`
2. Follow scikit-learn interface
3. Add to algorithm choices

## Monitoring

### Metrics Tracked
- Test selection accuracy
- Time savings
- False negative rate (missed failures)
- Model performance metrics

### Logging
- Selection decisions
- Model predictions
- Execution times
- Error conditions
