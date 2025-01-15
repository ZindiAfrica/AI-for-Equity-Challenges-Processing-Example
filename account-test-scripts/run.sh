#!/bin/bash
set -e

# Install uv if not present
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    uv venv
fi
source .venv/bin/activate

# Install dependencies
uv pip install boto3 pytest
uv pip install -e .

# Run the test runner with improved error handling
if ! python test_runner.py; then
    echo "❌ Tests failed! Check the output above for details."
    exit 1
fi
