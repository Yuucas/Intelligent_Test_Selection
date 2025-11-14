@echo off
REM Intelligent Test Selection - Quick Start Script for Windows

echo ==========================================
echo   Intelligent Test Selection
echo   Quick Start Script
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Create necessary directories
echo Creating directories...
if not exist "data\test_history" mkdir data\test_history
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs
echo Directories created
echo.

REM Generate test history
echo ==========================================
echo Step 1: Generate Test History
echo ==========================================
python src\main.py --mode generate-history --num-runs 100
echo.

REM Train model
echo ==========================================
echo Step 2: Train ML Model
echo ==========================================
python src\main.py --mode train
echo.

REM Test selection
echo ==========================================
echo Step 3: Select Tests
echo ==========================================
python src\main.py --mode select --threshold 0.7
echo.

REM Generate report
echo ==========================================
echo Step 4: Generate Report
echo ==========================================
python src\main.py --mode report
echo.

echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo You can now:
echo   1. Run tests with: pytest --its-enabled --its-threshold 0.7
echo   2. View report: type test_selection_report.md
echo   3. Run demo: python demo.py
echo.
echo For more information, see:
echo   - README.md - Overview
echo   - USAGE.md - Detailed usage
echo   - ARCHITECTURE.md - System design
echo.
pause
