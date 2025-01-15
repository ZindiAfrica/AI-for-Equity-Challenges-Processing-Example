import boto3
import os
from typing import Dict, Optional

class AWSTestRunner:
    def __init__(self):
        self.credentials: Optional[Dict[str, str]] = None
        
    def get_credentials(self) -> Dict[str, str]:
        """Get AWS credentials from user if not already stored."""
        if not self.credentials:
            print("\nPlease enter your AWS credentials:")
            self.credentials = {
                'aws_access_key_id': input("AWS Access Key ID: ").strip(),
                'aws_secret_access_key': input("AWS Secret Access Key: ").strip(),
                'region_name': os.environ.get('AWS_REGION', 'us-east-2')
            }
            # Validate credentials
            try:
                sts = boto3.client('sts', **self.credentials)
                sts.get_caller_identity()
                print("✅ AWS credentials validated successfully!")
            except Exception as e:
                print(f"❌ Invalid AWS credentials: {e}")
                self.credentials = None
                return self.get_credentials()
        return self.credentials

    def run_s3_tests(self) -> None:
        """Run S3 access tests."""
        print("\nRunning S3 tests...")
        from testS3 import main
        main(self.get_credentials())

    def run_sagemaker_tests(self) -> None:
        """Run SageMaker access tests."""
        print("\nRunning SageMaker tests...")
        from testSageMaker import main
        main(self.get_credentials())

    def show_menu(self) -> None:
        """Display interactive menu for test selection."""
        while True:
            print("\nAWS Access Test Menu:")
            print("1. Test S3 Access")
            print("2. Test SageMaker Access")
            print("3. Run All Tests")
            print("4. Exit")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                self.run_s3_tests()
            elif choice == "2":
                self.run_sagemaker_tests()
            elif choice == "3":
                self.run_s3_tests()
                self.run_sagemaker_tests()
            elif choice == "4":
                print("\nExiting...")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    runner = AWSTestRunner()
    runner.show_menu()
