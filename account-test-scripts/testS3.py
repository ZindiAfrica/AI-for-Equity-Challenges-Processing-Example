import boto3
import os

def main():
  # Request AWS credentials and bucket name from the user
  aws_access_key_id = input("Enter your AWS_ACCESS_KEY_ID: ").strip()
  aws_secret_access_key = input("Enter your AWS_SECRET_ACCESS_KEY: ").strip()
  bucket_name = input("Enter your S3 bucket name: ").strip()

  # Initialize the S3 client
  s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
  )

  # File details
  test_file_name = "test_file.txt"
  test_content = "This is a test file for S3 operations."

  try:
    # Step 1: Create a test text file
    with open(test_file_name, "w") as file:
      file.write(test_content)
    print(f"Test file '{test_file_name}' created locally.")

    # Step 2: Upload the test file to the S3 bucket
    s3_client.upload_file(test_file_name, bucket_name, test_file_name)
    print(f"Test file '{test_file_name}' uploaded to bucket '{bucket_name}'.")

    # Step 3: Download the test file from the S3 bucket
    download_file_name = f"downloaded_{test_file_name}"
    s3_client.download_file(bucket_name, test_file_name, download_file_name)
    print(f"Test file '{test_file_name}' downloaded from bucket as '{download_file_name}'.")

    # Step 4: Delete the test file from the S3 bucket
    s3_client.delete_object(Bucket=bucket_name, Key=test_file_name)
    print(f"Test file '{test_file_name}' deleted from bucket '{bucket_name}'.")

  except Exception as e:
    print(f"An error occurred: {e}")

  finally:
    # Clean up local files
    if os.path.exists(test_file_name):
      os.remove(test_file_name)
      print(f"Local test file '{test_file_name}' deleted.")
    if os.path.exists(download_file_name):
      os.remove(download_file_name)
      print(f"Downloaded test file '{download_file_name}' deleted.")

if __name__ == "__main__":
  main()
