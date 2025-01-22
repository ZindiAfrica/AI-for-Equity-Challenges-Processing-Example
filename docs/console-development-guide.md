# Local Development Guide

This guide covers how to develop and run the ML pipeline on your local machine. Choose this approach if you:

- Want to develop with your preferred local Python environment
- Need direct access to AWS resources through the console
- Want to debug code locally before deploying to SageMaker
- Prefer command line tools over web interfaces

## Prerequisites

1. AWS CLI installed and configured with appropriate credentials
2. Python 3.10.0 or higher installed locally
3. Docker installed and running (for container builds)
4. uv package manager installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

1. Clone the repository and install dependencies:

```bash
git clone git@github.com:ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git
cd sua-outsmarting-outbreaks
./setup.sh
```

## Development Workflow

1. Activate the virtual environment:

```bash
source .venv/bin/activate
```

2. Configure your AWS credentials:

```bash
# Option 1: Using environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-2

# Option 2: Using AWS CLI profiles
aws configure --profile sua-competition
export AWS_PROFILE=sua-competition
```

3. Run code quality checks:

```bash
# Format code
ruff format .

# Run linting
ruff check .

# Run tests
pytest
```

4. Build and test Docker image locally:

```bash
# Build image
docker compose build

# Run debug container
docker compose up dev
```

## Running the Pipeline

1. Run the full pipeline:

```bash
python build_and_run_aws.py
```

This will:

- Build and push the Docker image to ECR
- Execute the SageMaker pipeline with all stages
- Save outputs to your team's S3 bucket

2. Run individual pipeline stages:

```bash
# Data preparation
python notebooks/outsmarting_data_prep.py

# Model training
python notebooks/outsmarting_train.py

# Model evaluation
python notebooks/outsmarting_eval.py

# Generate predictions
python notebooks/outsmarting_predict.py
```

## Project Structure

```
.
├── notebooks/           # Pipeline stage implementations
├── tests/              # Unit and integration tests
├── utils/              # Shared utility functions
├── Dockerfile          # Container definition
├── pyproject.toml      # Dependencies and build config
└── setup.sh           # Development environment setup
```

## Monitoring and Debugging

1. View pipeline progress:

   - AWS Console -> SageMaker -> Processing jobs
   - CloudWatch logs for detailed execution logs
   - S3 bucket for stage outputs and artifacts

2. Debug locally:

   - Use debug_entry.py for interactive container debugging
   - Check Docker logs: `docker compose logs dev`
   - Monitor resource usage: `docker stats`

3. Common issues:
   - Check troubleshooting guide for known issues
   - Verify AWS credentials and permissions
   - Ensure Docker daemon is running
   - Check S3 bucket permissions
