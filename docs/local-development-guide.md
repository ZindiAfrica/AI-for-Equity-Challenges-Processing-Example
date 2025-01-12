# Using AWS Console and Local Development

## Prerequisites

1. AWS CLI configured with your credentials
2. Python 3.10.0 or higher installed locally
3. Docker installed and running
4. uv package manager installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Virtual Environment Setup

We strongly recommend using a virtual environment for development:

1. Create and activate a new virtual environment using uv:
```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies and development tools:
```bash
# Install main package and dev dependencies
uv pip install -e ".[dev]"

# Verify key packages are installed
python -c "import boto3, sagemaker, pandas, sklearn, joblib"

# Install pre-commit hooks
pre-commit install
```

3. Run code quality checks:
```bash
ruff check --fix .
ruff format .
```

## Setup Instructions

2. Configure AWS credentials in your environment:
```bash
# Set up AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-2
```

3. Run the pipeline:
```python
python build_and_run_aws.py
```

## Output Locations

Results are saved to your team's S3 bucket:
- Processed data: `s3://<team-bucket>/output/data_prep/`
- Trained model: `s3://<team-bucket>/output/training/`
- Evaluation results: `s3://<team-bucket>/output/evaluation/`
- Final predictions: `s3://<team-bucket>/output/predictions/`

## Project Structure

The project uses modern Python packaging with pyproject.toml:
- Dependencies are managed in pyproject.toml
- Development tools (ruff, pytest, etc.) are included in [dev] extras
- Code quality is enforced via ruff and pre-commit hooks
- Tests are managed with pytest

To add new dependencies:
1. Add them to pyproject.toml
2. Reinstall the package: `uv pip install -e ".[dev]"`

## Resource Configuration

The pipeline uses optimized instances for each stage:

Data Preparation:
- Instance: ml.m5.2xlarge ($0.519/hr)
- Storage: 100GB EBS volume
- Network: Up to 10 Gigabit
- Runtime: ~2 hours

Training:
- Instance: ml.g4dn.8xlarge ($2.176/hr)
- GPU: NVIDIA T4 (16GB)
- Memory: 128GB RAM
- Storage: 100GB EBS volume
- Network: 50 Gigabit
- Runtime: ~4-6 hours

Evaluation/Prediction:
- Instance: ml.m5.xlarge ($0.672/hr)
- Memory: 16GB RAM
- Storage: 100GB EBS volume
- Network: Up to 10 Gigabit
- Runtime: ~1 hour

Cost Optimization:
- Uses Spot instances when possible (up to 70% savings)
- Automatic shutdown after completion
- Maximum runtime limit: 24 hours

## Monitoring

Monitor job progress in:
1. SageMaker Studio interface
2. SageMaker console -> Processing jobs
3. CloudWatch logs
