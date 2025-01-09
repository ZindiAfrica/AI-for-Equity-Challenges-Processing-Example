#!/bin/bash

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws configure list &> /dev/null; then
    echo "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create and activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies using uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create necessary S3 buckets if they don't exist
aws s3 mb s3://sua-outsmarting-outbreaks-challenge-comp --region us-east-2 || true
aws s3 mb s3://comp-user-5ow9bw-team-bucket --region us-east-2 || true

echo "Setup complete! You can now run the example notebooks."
echo "Remember to activate the virtual environment with: source .venv/bin/activate"
