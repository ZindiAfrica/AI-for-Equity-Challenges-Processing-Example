# AWS Account Test Scripts

This directory contains scripts for testing AWS account access and permissions. The test suite includes comprehensive checks for both S3 and SageMaker services.

## Features

### Interactive Test Runner
- Menu-driven interface for running tests
- Credential validation and persistence
- Option to run individual or all tests
- Clear progress indicators and error messages

### S3 Tests (`testS3.py`)
- Automatic username and bucket name detection
- Complete S3 operation validation:
  1. Local file creation
  2. File upload to S3
  3. Bucket content listing
  4. File download
  5. Content verification
  6. Object deletion
  7. Local cleanup
- Team bucket name validation (format: `comp-user-XXXXXX-team-bucket`)

### SageMaker Tests (`testSageMaker.py`)
- Comprehensive SageMaker access verification:
  1. Studio domain access
  2. Notebook instance availability
  3. Processing job permissions
  4. Training job access
  5. Model deployment capabilities
  6. Endpoint accessibility
- Detailed error reporting and troubleshooting guidance
- Recent job history analysis (last 24 hours)
- Failed job detection and reporting

## Prerequisites

- Python 3.10 or higher
- AWS credentials (Access Key ID and Secret Access Key)
- `uv` package manager (auto-installed by run script)

## Quick Start

1. Run the test suite:
```bash
./run.sh
```

2. Select test option from menu:
```
AWS Access Test Menu:
1. Test S3 Access
2. Test SageMaker Access
3. Run All Tests
4. Exit
```

3. Enter AWS credentials when prompted:
```
Please enter your AWS credentials:
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
```

## Project Structure

```
account-test-scripts/
├── pyproject.toml     # Project dependencies
├── README.md         # This documentation
├── run.sh           # Setup and execution script
├── test_runner.py   # Interactive test menu
├── testS3.py        # S3 access tests
└── testSageMaker.py # SageMaker access tests
```

## Development

### Dependencies
- Managed via `pyproject.toml`
- Core requirements:
  - boto3: AWS SDK
  - pytest: Testing framework
- Dev dependencies available

### Virtual Environment
- Created automatically by `run.sh`
- Uses `uv` for dependency management
- Located in `.venv` directory

### Adding Dependencies
1. Edit `pyproject.toml`
2. Run `./run.sh` to update environment

## Troubleshooting

### Credential Issues
- Verify AWS Access Key ID and Secret Access Key
- Ensure proper IAM permissions
- Check AWS region setting (default: us-east-2)

### S3 Access Problems
- Validate bucket name format
- Check bucket existence and permissions
- Review IAM policies for S3 access

### SageMaker Access Issues
- Verify SageMaker permissions in IAM
- Check service quotas and limits
- Review recent job failures in logs

### Script Execution Errors
- Ensure Python 3.10+ is installed
- Check virtual environment activation
- Verify network connectivity
- Review error messages for details

## Error Messages

The scripts provide detailed error messages and troubleshooting tips:

- Credential validation failures
- Permission denied errors
- Resource access issues
- Service-specific error details

Example error output:
```
❌ Error occurred: AccessDenied
Troubleshooting tips:
1. Verify your IAM user has appropriate permissions
2. Check if you need additional IAM policies
3. Ensure you're using the correct AWS region
4. Contact support if you need policy adjustments
```
