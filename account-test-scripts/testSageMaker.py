import boto3
import json
from typing import List, Dict
from datetime import datetime, timezone

def print_step(step_num: int, desc: str) -> None:
    """Print a formatted step header."""
    print(f"\n{'='*80}\nStep {step_num}: {desc}\n{'='*80}")

def get_test_steps() -> List[str]:
    """Return list of test steps for display."""
    return [
        "Check SageMaker Studio domain access",
        "List available notebook instances", 
        "Check processing job permissions",
        "Verify training job access",
        "Test model deployment permissions",
        "Validate endpoint access"
    ]

def format_response(response: Dict) -> str:
    """Format API response for display."""
    return json.dumps(response, indent=2, default=str)

def main():
    # Print test overview
    steps = get_test_steps()
    print("\nSageMaker Access Test Steps:")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
    print("\nStarting test execution...\n")

    # Request AWS credentials from the user
    aws_access_key_id = input("Enter your AWS_ACCESS_KEY_ID: ").strip()
    aws_secret_access_key = input("Enter your AWS_SECRET_ACCESS_KEY: ").strip()

    # Initialize the SageMaker client
    sagemaker_client = boto3.client(
        'sagemaker',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        # Step 1: Check SageMaker Studio domain access
        print_step(1, "Checking SageMaker Studio domain access")
        domains = sagemaker_client.list_domains()
        print("✓ Found domains:")
        print(format_response(domains))

        # Step 2: List notebook instances
        print_step(2, "Listing available notebook instances")
        notebooks = sagemaker_client.list_notebook_instances()
        print("✓ Found notebook instances:")
        print(format_response(notebooks))

        # Step 3: Check processing job permissions
        print_step(3, "Checking processing job permissions")
        processing_jobs = sagemaker_client.list_processing_jobs(
            CreationTimeAfter=datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
        print("✓ Recent processing jobs:")
        print(format_response(processing_jobs))

        # Step 4: Verify training job access
        print_step(4, "Verifying training job access")
        training_jobs = sagemaker_client.list_training_jobs(
            CreationTimeAfter=datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
        print("✓ Recent training jobs:")
        print(format_response(training_jobs))

        # Step 5: Test model deployment permissions
        print_step(5, "Testing model deployment permissions")
        models = sagemaker_client.list_models()
        print("✓ Available models:")
        print(format_response(models))

        # Step 6: Validate endpoint access
        print_step(6, "Validating endpoint access")
        endpoints = sagemaker_client.list_endpoints()
        print("✓ Available endpoints:")
        print(format_response(endpoints))

        print("\n✅ All SageMaker access tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        if "AccessDenied" in str(e):
            print("\nTroubleshooting tips:")
            print("1. Verify your IAM user has appropriate SageMaker permissions")
            print("2. Check if you need additional IAM policies")
            print("3. Ensure you're using the correct AWS region")
            print("4. Contact support if you need policy adjustments")

if __name__ == "__main__":
    main()
