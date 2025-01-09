# Troubleshooting Guide

## Common Issues

### 1. Package Installation Fails
- Try restarting the kernel
- Check internet connectivity
- If using pip, try switching to uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Verify uv is working: `uv --version`
- Check Python version: `python --version` (should be 3.10.0 or higher)
- For development dependencies, install with: `uv pip install ".[dev]"`

### 2. Code Quality Checks Fail
- Run `ruff check .` to see detailed linting errors
- Run `ruff format .` to automatically fix formatting
- Ensure pre-commit hooks are installed: `pre-commit install`
- Run pre-commit manually: `pre-commit run --all-files`

### 2. AWS Credential Issues
- Verify AWS credentials are properly set in environment:
  ```bash
  aws configure list
  aws sts get-caller-identity
  ```
- Check S3 bucket permissions with:
  ```bash
  aws s3 ls s3://comp-user-5ow9bw-team-bucket
  ```
- Ensure Docker has access to AWS credentials
- Verify SageMaker execution role permissions

### 3. Resource Limits
- Check if you've hit the team's GPU instance quota
- Monitor cost usage in AWS Cost Explorer
- Contact competition organizers if needed

## Security Notes

- All resources are tagged with your team name
- Access is restricted to your team's resources
- Data is encrypted in transit and at rest
- Credentials are managed through AWS IAM
