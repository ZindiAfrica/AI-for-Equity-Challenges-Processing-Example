# Using AWS Console and Local Development

## Prerequisites

1. AWS CLI configured with your credentials
2. Python 3.10.0 or higher installed locally
3. Docker installed and running
4. uv package manager installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Development Options

You can develop either using a local virtual environment or Docker. Choose the method that works best for you.

### Option 1: Docker Development

1. Build and run using docker compose:
```bash
docker compose build
docker compose up
```

2. Set your AWS credentials as environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-2
```

3. Push to ECR (if needed):
```bash
./build_and_push.sh
```

### Option 2: Virtual Environment Setup

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

# Install pre-commit hooks
pre-commit install
```

3. Run code quality checks:
```bash
ruff check .
ruff format .
```

4. Run tests:
```bash
pytest
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd sua-outsmarting-outbreaks-example
```

2. Configure AWS credentials in your environment:
```bash
# Set up AWS credentials
aws configure

# Or use a specific profile
export AWS_PROFILE=your-profile-name
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

The pipeline uses:
- GPU instance: ml.g4dn.8xlarge
- 100GB storage volume
- Maximum runtime: 24 hours

## Monitoring

Monitor job progress in:
1. SageMaker Studio interface
2. SageMaker console -> Processing jobs
3. CloudWatch logs
