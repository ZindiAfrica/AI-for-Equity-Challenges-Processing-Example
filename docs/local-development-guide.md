# Local Development Guide

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

1. Clone the repository:
```bash
git clone https://github.com/ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git
cd AI-for-Equity-Challenges-Processing-Example
```

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

## Development Workflow

1. Create a new feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and run tests:
```bash
pytest
ruff check .
ruff format .
```

3. Commit your changes:
```bash
git add .
git commit -m "feat: your feature description"
```

4. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Resource Configuration

The pipeline uses optimized instances for each stage:

Data Preparation:
- Instance: ml.m5.2xlarge ($0.46/hr on-demand, $0.138/hr spot)
- Storage: 100GB EBS volume
- Network: Up to 10 Gigabit
- Runtime: ~2 hours

Training:
- Instance: ml.g4dn.8xlarge ($2.72/hr on-demand, $0.816/hr spot)
- GPU: NVIDIA T4 (16GB)
- Memory: 128GB RAM
- Storage: 100GB EBS volume
- Network: 50 Gigabit
- Runtime: ~4-6 hours

Evaluation/Prediction:
- Instance: ml.m5.xlarge ($0.23/hr on-demand, $0.069/hr spot)
- Memory: 16GB RAM
- Storage: 100GB EBS volume
- Network: Up to 10 Gigabit
- Runtime: ~1 hour

Cost Optimization:
- Uses Spot instances when possible (up to 70% savings)
- Automatic shutdown after completion
- Maximum runtime limit: 24 hours
- Resource monitoring and alerts
- Cost allocation tags

## Local Testing

1. Run unit tests:
```bash
pytest tests/
```

2. Run integration tests:
```bash
pytest tests/integration/
```

3. Test Docker build:
```bash
docker compose build
docker compose up dev
```

4. Test pipeline stages locally:
```bash
python -m sua_outsmarting_outbreaks.run_local --stage data-prep
python -m sua_outsmarting_outbreaks.run_local --stage train
python -m sua_outsmarting_outbreaks.run_local --stage evaluate
python -m sua_outsmarting_outbreaks.run_local --stage predict
```

## Monitoring

Monitor job progress in:
1. SageMaker Studio interface
2. SageMaker console -> Processing jobs
3. CloudWatch logs
4. CloudWatch metrics
5. Cost Explorer
6. AWS Health Dashboard
