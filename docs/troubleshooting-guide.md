# Troubleshooting Guide

## Common Issues

### 1. Package Installation Fails

- Try restarting the kernel
- Check internet connectivity
- Install uv if not present: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Verify uv is working: `uv --version`
- Check Python version: `python --version` (should be 3.10.0 or higher)
- For development dependencies: `uv pip install -e ".[dev]"`
- For system-wide installation: `uv pip install -e ".[dev]" --system`
- Clear pip cache if needed: `uv cache clear`

### 2. Code Quality Checks Fail

- Run `ruff check .` to see detailed linting errors
- Run `ruff format .` to automatically fix formatting
- Ensure pre-commit hooks are installed: `pre-commit install`
- Run pre-commit manually: `pre-commit run --all-files`
- Update ruff if needed: `uv pip install -U ruff`

### 3. AWS Credential Issues

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
- Check AWS CLI version: `aws --version`
- Verify region setting: `aws configure get region`

### 4. Docker Issues

- Verify Docker daemon is running: `docker info`
- Check Docker version: `docker version`
- Ensure enough disk space: `docker system df`
- Clean up unused images: `docker system prune`
- Check Docker logs: `docker logs <container-id>`

### 5. Resource Limits

- Check if you've hit the team's GPU instance quota
- Monitor cost usage in AWS Cost Explorer
- Contact competition organizers if needed
- Check CloudWatch metrics for resource utilization
- Review SageMaker instance availability in your region

### 6. Data Pipeline Issues

- Verify input data exists and is readable
- Check output paths are writable
- Monitor CloudWatch logs for errors
- Verify model artifacts are saved correctly
- Check disk space on SageMaker instances

## Security Notes

- All resources are tagged with your team name
- Access is restricted to your team's resources
- Data is encrypted in transit and at rest
- Credentials are managed through AWS IAM
- Regular security audits are performed
- MFA is required for AWS Console access
