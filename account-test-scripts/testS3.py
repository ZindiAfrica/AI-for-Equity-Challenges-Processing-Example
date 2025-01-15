import boto3
import os
from typing import List

def print_step(step_num: int, desc: str) -> None:
    """Print a formatted step header."""
    print(f"\n{'='*80}\nStep {step_num}: {desc}\n{'='*80}")

def get_test_steps() -> List[str]:
    """Return list of test steps for display."""
    return [
        "Create local test file",
        "Upload file to S3",
        "List bucket contents",
        "Download file from S3",
        "Verify file contents",
        "Delete file from S3",
        "Clean up local files"
    ]

def main(credentials=None):
    # Print test overview
    steps = get_test_steps()
    print("\nS3 Connection Test Steps:")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
    print("\nStarting test execution...\n")

    # Use provided credentials or request from user
    if not credentials:
        credentials = {
            'aws_access_key_id': input("Enter your AWS_ACCESS_KEY_ID: ").strip(),
            'aws_secret_access_key': input("Enter your AWS_SECRET_ACCESS_KEY: ").strip()
        }

    # Initialize the S3 client
    s3_client = boto3.client('s3', **credentials)

    # Get caller identity to fetch username
    sts_client = boto3.client(
        'sts',
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key']
    )
    
    try:
        # Get the IAM username from the caller identity
        caller_identity = sts_client.get_caller_identity()
        arn = caller_identity['Arn']
        username = arn.split('/')[-1]  # Extract username from ARN
        
        # Validate username format
        if not username.startswith('comp-user-'):
            raise ValueError(f"Invalid username format: {username}. Expected format: comp-user-XXXXXX")
            
        # Construct expected bucket name
        bucket_name = f"{username}-team-bucket"
        print(f"\nDetected username: {username}")
        print(f"Using bucket name: {bucket_name}")
            
    except Exception as e:
        print(f"Error getting username: {e}")
        raise

    # File details
    test_file_name = "test_file.txt"
    test_content = "This is a test file for S3 operations."
    download_file_name = f"downloaded_{test_file_name}"

    try:
        # Step 1: Create a test text file
        print_step(1, "Creating local test file")
        with open(test_file_name, "w") as file:
            file.write(test_content)
        print(f"✓ Created local file: {test_file_name}")
        print(f"✓ File contents: {test_content}")

        # Step 2: Upload the test file to the S3 bucket
        print_step(2, "Uploading file to S3")
        s3_client.upload_file(test_file_name, bucket_name, test_file_name)
        print(f"✓ Uploaded {test_file_name} to s3://{bucket_name}/{test_file_name}")

        # Step 3: List bucket contents
        print_step(3, "Listing bucket contents")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=test_file_name)
        for obj in response.get('Contents', []):
            print(f"✓ Found in bucket: {obj['Key']} (size: {obj['Size']} bytes)")

        # Step 4: Download the test file from the S3 bucket
        print_step(4, "Downloading file from S3")
        s3_client.download_file(bucket_name, test_file_name, download_file_name)
        print(f"✓ Downloaded to: {download_file_name}")

        # Step 5: Verify contents
        print_step(5, "Verifying file contents")
        with open(download_file_name, 'r') as file:
            downloaded_content = file.read()
        if downloaded_content == test_content:
            print("✓ File contents match original")
        else:
            print("✗ File contents do not match!")
            print(f"Original: {test_content}")
            print(f"Downloaded: {downloaded_content}")

        # Step 6: Delete the test file from the S3 bucket
        print_step(6, "Deleting file from S3")
        s3_client.delete_object(Bucket=bucket_name, Key=test_file_name)
        print(f"✓ Deleted {test_file_name} from bucket")

        # Step 7: Clean up local files
        print_step(7, "Cleaning up local files")
        if os.path.exists(test_file_name):
            os.remove(test_file_name)
            print(f"✓ Deleted local file: {test_file_name}")
        if os.path.exists(download_file_name):
            os.remove(download_file_name)
            print(f"✓ Deleted downloaded file: {download_file_name}")

        print("\n✅ All steps completed successfully!")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
