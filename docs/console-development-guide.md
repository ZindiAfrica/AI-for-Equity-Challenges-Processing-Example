# Local Development with AWS Console

This guide covers how to develop and run the ML pipeline directly on your local machine using the AWS Console for resource management. This approach is suitable if you:
- Prefer working directly with Python on your local machine
- Want direct access to AWS resources through the console
- Need to debug code locally before deploying

## Prerequisites

1. AWS CLI configured with your credentials
2. Python 3.10.0 or higher installed locally
3. uv package manager installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup Instructions

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

3. Configure AWS credentials in your environment:
```bash
# Set up AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-2

# Note: The code will use your team's assigned S3 bucket in the format:
# {workspace}-team-bucket
# Do not create your own buckets - only use the team bucket
```

4. Run code quality checks:
```bash
ruff check .
ruff format .
```

5. Run the pipeline (this will build the Docker image and execute the SageMaker pipeline):
```python
python build_and_run_aws.py
```

Note: The script handles both building/pushing the Docker image and executing the SageMaker pipeline in one step.

## Project Structure

The project uses modern Python packaging with pyproject.toml:
- Dependencies are managed in pyproject.toml
- Development tools (ruff, pytest, etc.) are included in [dev] extras
- Code quality is enforced via ruff and pre-commit hooks
- Tests are managed with pytest

To add new dependencies:
1. Add them to pyproject.toml
2. Reinstall the package: `uv pip install -e ".[dev]"`

## Monitoring

Monitor job progress in:
1. AWS Console -> SageMaker -> Processing jobs
2. CloudWatch logs
3. S3 bucket for output files
