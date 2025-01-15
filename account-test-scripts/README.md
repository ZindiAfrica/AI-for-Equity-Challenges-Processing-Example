# AWS Account Test Scripts

This directory contains scripts for testing AWS account access and S3 bucket operations.

## S3 Test Script

The `testS3.py` script validates your AWS credentials and tests basic S3 operations using your team bucket.

### Features

- Automatic username detection from AWS credentials
- Team bucket name validation (must follow pattern: `comp-user-XXXXXX-team-bucket`)
- Step-by-step testing of S3 operations:
  1. Create local test file
  2. Upload file to S3
  3. List bucket contents
  4. Download file from S3
  5. Verify file contents
  6. Delete file from S3
  7. Clean up local files
- Clear progress indicators and error messages
- Automatic cleanup of test files

### Prerequisites

- Python 3.10 or higher
- AWS credentials (Access Key ID and Secret Access Key)
- uv package manager (installed automatically by run script)

### Usage

1. Run the test script:
```bash
./run.sh
```

2. When prompted, enter your AWS credentials:
```
Enter your AWS_ACCESS_KEY_ID: YOUR_ACCESS_KEY
Enter your AWS_SECRET_ACCESS_KEY: YOUR_SECRET_KEY
```

3. The script will:
   - Detect your username from the credentials
   - Construct your expected team bucket name
   - Ask for confirmation or alternative bucket name
   - Run through all test steps
   - Clean up any test files

### Example Output

```
S3 Connection Test Steps:
1. Create local test file
2. Upload file to S3
3. List bucket contents
4. Download file from S3
5. Verify file contents
6. Delete file from S3
7. Clean up local files

Detected username: comp-user-3u7m86
Expected bucket name: comp-user-3u7m86-team-bucket

Use bucket 'comp-user-3u7m86-team-bucket'? [Y/n]:
```

### Troubleshooting

1. Invalid Credentials
   - Verify your AWS Access Key ID and Secret Access Key
   - Ensure credentials have S3 permissions
   - Check AWS region setting

2. Bucket Access Issues
   - Confirm bucket name matches pattern: `{username}-team-bucket`
   - Verify bucket exists and you have access
   - Check S3 permissions in IAM

3. Script Failures
   - Check Python version: `python --version`
   - Verify boto3 installation
   - Check network connectivity
   - Review error messages for details

### Development

The project uses:
- `pyproject.toml` for dependency management
- `uv` for package installation
- `boto3` for AWS operations

To add dependencies:
1. Edit `pyproject.toml`
2. Run `./run.sh` to update environment
