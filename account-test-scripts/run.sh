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
uv pip install -e .

# Run the test script
python testS3.py
