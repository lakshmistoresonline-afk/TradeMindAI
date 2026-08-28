#!/bin/bash

echo "Starting TradeMind AI Test Suite..."

# Run pytest with coverage report
python -m pytest tests/ --cov=backend/ --cov-report=term-missing

echo "Testing Complete."
