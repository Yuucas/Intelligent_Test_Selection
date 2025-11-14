# CI/CD Workflow Guide

## GitHub Actions Workflow Explained

This document explains how the Intelligent Test Selection system works in CI/CD pipelines.

## Workflow Logic

### Smart Detection of Changes

The workflow now intelligently handles different scenarios:

#### Scenario 1: Code Changes Detected ✅
When Python files are modified:
1. **Detect Changes**: Compare current commit with base
2. **Analyze Impact**: Determine which tests are affected
3. **Select Tests**: ML model chooses optimal subset
4. **Run Selected**: Execute only necessary tests
5. **Generate Report**: Document selection decisions

**Example:**
```
Changed files: src/auth.py, src/database.py
→ ITS selects 5 out of 43 tests
→ Runs in 1.5s instead of 12s
→ 87% time saved
```

#### Scenario 2: No Code Changes ✅
When only documentation or config files change:
1. **Detect No Changes**: No Python files modified
2. **Run Full Suite**: Execute all tests for verification
3. **Skip ITS**: No need for selection
4. **Faster Pipeline**: No ML overhead

**Example:**
```
Changed files: README.md, .github/workflows/ci.yml
→ No Python changes detected
→ Runs full test suite (43 tests)
→ Ensures everything still works
```

## Workflow Steps

### 1. Setup Phase
```yaml
- Checkout code (with full history)
- Setup Python 3.9
- Cache dependencies
- Install requirements
```

### 2. Model Preparation
```yaml
- Check if trained model exists
- If not: Generate test history
- If not: Train ML model
- Model cached for future runs
```

### 3. Change Detection (New!)
```yaml
- Detect changed Python files
- Compare with base branch (PR) or previous commit (push)
- Set flag: has_changes=true/false
```

### 4. Test Execution

#### Path A: No Changes
```yaml
IF no Python changes:
  → Run full test suite
  → pytest tests/sample_project -v
  → Ensures baseline quality
  → Fast completion
```

#### Path B: Changes Detected
```yaml
IF Python changes detected:
  → Run ITS selection
  → python src/main.py --mode select
  → Run selected tests only
  → Generate selection report
```

### 5. Reporting
```yaml
- Upload test reports (if generated)
- Upload coverage reports
- Comment on PR with results
- Save artifacts for review
```

## Handling Edge Cases

### Edge Case 1: No Tests Selected
```yaml
IF ITS selects 0 tests:
  → Fallback to full test suite
  → Prevents "no tests collected" error
  → Ensures tests always run
```

### Edge Case 2: Model Not Trained
```yaml
IF model doesn't exist:
  → Generate synthetic history
  → Train model on the fly
  → Cache for future runs
  → Continue with workflow
```

### Edge Case 3: Only Doc Changes
```yaml
IF only .md or .yml files changed:
  → No Python changes detected
  → Run full suite for verification
  → Skip ITS overhead
  → Exit successfully
```

## Performance Comparison

### Traditional CI/CD
```
Every commit:
  → Runs all 43 tests
  → Takes ~12 seconds
  → Uses full resources
  → No optimization
```

### With Intelligent Test Selection
```
Doc changes:
  → Runs all 43 tests
  → Takes ~12 seconds
  → No ITS overhead

Code changes:
  → ITS selects 5-10 tests
  → Takes ~2 seconds
  → 83% time saved
  → Smart optimization
```

## Configuration Options

### Adjust Selection Threshold

In `.github/workflows/its-ci.yml`:

```yaml
# Conservative (more tests)
python src/main.py --mode select --threshold 0.5

# Balanced (default)
python src/main.py --mode select --threshold 0.7

# Aggressive (fewer tests)
python src/main.py --mode select --threshold 0.9
```

### Adjust Failure Tolerance

```yaml
# Stop on first failure
pytest -v --maxfail=1

# Stop after 5 failures (default)
pytest -v --maxfail=5

# Never stop
pytest -v
```

## Monitoring & Debugging

### View Selection Decisions

Check the GitHub Actions logs:
```
1. Go to Actions tab
2. Click on workflow run
3. Expand "Select and run tests" step
4. See selected tests and reasoning
```

### Download Reports

Artifacts available after each run:
- `test-selection-report` - Selection decisions
- `coverage-report` - Code coverage results

### Debug Mode

Enable detailed logging:
```yaml
env:
  ITS_LOG_LEVEL: DEBUG
```

## Best Practices

### 1. Branch Protection Rules
```
Require status checks:
  ✓ intelligent-test-selection
  ✓ All checks must pass
```

### 2. Periodic Full Suite Runs
```yaml
# Run full suite nightly
on:
  schedule:
    - cron: '0 0 * * *'  # Midnight daily
```

### 3. Model Retraining
```yaml
# Retrain monthly with latest data
on:
  schedule:
    - cron: '0 0 1 * *'  # First of month
```

### 4. Monitor False Negatives
```
Track metrics:
  - Tests skipped that later fail
  - Adjust threshold if needed
  - Review selection accuracy
```

## Troubleshooting

### Issue: "No tests collected"
**Cause**: ITS selected 0 tests
**Fix**: ✅ Already handled - fallback to full suite

### Issue: "Model not found"
**Cause**: First run or cache cleared
**Fix**: ✅ Workflow trains model automatically

### Issue: "Too many tests selected"
**Cause**: Threshold too low
**Solution**: Increase threshold in workflow

### Issue: "Missing dependencies"
**Cause**: Cache invalidated
**Solution**: Workflow reinstalls automatically

## Metrics to Track

### Selection Efficiency
```
- Average tests selected
- Average time saved
- Test reduction percentage
```

### Accuracy Metrics
```
- False negatives (missed failures)
- False positives (unnecessary tests)
- Selection precision
```

### Performance Metrics
```
- Workflow duration
- Test execution time
- Cache hit rate
```

## Example Workflow Run

### Pull Request with Auth Changes

```
1. Trigger: PR created with auth.py changes

2. Setup (30s):
   - Checkout code
   - Setup Python
   - Install dependencies

3. Model Check (2s):
   - Model exists ✓
   - Load from cache ✓

4. Change Detection (1s):
   - Changed: src/auth.py
   - Changed: tests/test_auth.py
   - has_changes=true ✓

5. Test Selection (3s):
   - Analyze impact
   - Predict failures
   - Select 8 tests

6. Run Tests (2s):
   - Execute 8 selected tests
   - All pass ✓

7. Report (1s):
   - Generate selection report
   - Upload artifacts
   - Comment on PR

Total: 39 seconds (vs 45s for full suite)
Savings: 6 seconds (13%)
```

### Push with Only README Changes

```
1. Trigger: Push to main (README.md updated)

2. Setup (30s):
   - Checkout code
   - Setup Python
   - Install dependencies

3. Model Check (2s):
   - Model exists ✓
   - Load from cache ✓

4. Change Detection (1s):
   - Changed: README.md
   - No Python files
   - has_changes=false ✓

5. Run Full Suite (12s):
   - Execute all 43 tests
   - All pass ✓
   - Verification complete

Total: 45 seconds
No ITS overhead ✓
```

## Integration with Other Tools

### SonarQube
```yaml
- name: SonarQube Scan
  run: |
    # Only scan changed files
    sonar-scanner -Dsonar.inclusions="$(cat changed_files.txt)"
```

### Code Coverage
```yaml
- name: Coverage Report
  run: |
    # Coverage for selected tests only
    pytest --cov --cov-report=xml
```

### Slack Notifications
```yaml
- name: Notify Slack
  if: failure()
  run: |
    # Send selection report to Slack
    cat test_selection_report.md | slack-cli
```

## Summary

The improved CI workflow:
- ✅ Handles all edge cases gracefully
- ✅ Never fails with "no tests collected"
- ✅ Runs full suite when appropriate
- ✅ Uses ITS only when beneficial
- ✅ Provides detailed reporting
- ✅ Optimizes for both speed and safety

**Result**: Faster pipelines without compromising quality! 🚀
