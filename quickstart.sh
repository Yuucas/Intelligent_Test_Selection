#!/bin/bash

# Intelligent Test Selection - Quick Start Script

echo "=========================================="
echo "  Intelligent Test Selection"
echo "  Quick Start Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data/test_history
mkdir -p data/models
mkdir -p logs
echo "Directories created"
echo ""

# Generate test history
echo "=========================================="
echo "Step 1: Generate Test History"
echo "=========================================="
python src/main.py --mode generate-history --num-runs 100
echo ""

# Train model
echo "=========================================="
echo "Step 2: Train ML Model"
echo "=========================================="
python src/main.py --mode train
echo ""

# Test selection
echo "=========================================="
echo "Step 3: Select Tests"
echo "=========================================="
python src/main.py --mode select --threshold 0.7
echo ""

# Generate report
echo "=========================================="
echo "Step 4: Generate Report"
echo "=========================================="
python src/main.py --mode report
echo ""

echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "You can now:"
echo "  1. Run tests with: pytest --its-enabled --its-threshold 0.7"
echo "  2. View report: cat test_selection_report.md"
echo "  3. Run demo: python demo.py"
echo ""
echo "For more information, see:"
echo "  • README.md - Overview"
echo "  • USAGE.md - Detailed usage"
echo "  • ARCHITECTURE.md - System design"
echo ""
