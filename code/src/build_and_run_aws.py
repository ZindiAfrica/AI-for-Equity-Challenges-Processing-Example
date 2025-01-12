import base64
import os
import subprocess
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv

from sua_outsmarting_outbreaks.utils.config import settings
from sua_outsmarting_outbreaks.utils.constants import MAX_RUNTIME_SECONDS
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor

from sua_outsmarting_outbreaks.utils.aws_utils import (
  get_execution_role,
  get_user_bucket_name,
  get_user_docker_image_tag,
  get_user_name,
  get_user_registry_name,
)

# Suppress specific pydantic warning
warnings.filterwarnings(
  "ignore",
  message='Field name "json" in "MonitoringDatasetFormat" shadows an attribute in parent "Base"'
)

try:
  import boto3
  import sagemaker
except ImportError:
  print("Required packages are missing. Please install them with:")
  print("pip install boto3 sagemaker")
  sys.exit(1)


def check_aws_environment():
  """Print AWS environment settings and handle AWS_PROFILE precedence"""
  aws_profile = os.environ.get("AWS_PROFILE", "")

  if aws_profile:
    print(f"Using AWS_PROFILE: {aws_profile}")
    # If AWS_PROFILE is set, unset other AWS environment variables
    for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]:
      if key in os.environ:
        del os.environ[key]
  else:
    # Print individual credentials if AWS_PROFILE is not set
    print(f"AWS_ACCESS_KEY_ID: {'*****' if os.environ.get('AWS_ACCESS_KEY_ID') else 'not set'}")
    print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'not set')}")
    print(
      f"AWS_SECRET_ACCESS_KEY: {'*****' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'not set'}")

  # Get and print current user identity
  try:
    sts = boto3.client("sts")
    caller_identity = sts.get_caller_identity()
    username = caller_identity["Arn"].split("/")[-1]
    print(f"AWS Username: {username}")
  except Exception as e:
    print(f"Failed to get AWS identity: {e}")


def get_account_id():
  sts = boto3.client("sts")
  return sts.get_caller_identity()["Account"]


def build_and_push_docker_image(image_name, account_id, region, image_tag):
  # Check if Docker daemon is running
  try:
    subprocess.run(["docker", "info"], check=True, capture_output=True)
  except subprocess.CalledProcessError:
    print("Error: Docker daemon is not running. Please start Docker and try again.")
    print("On macOS, launch Docker Desktop from Applications.")
    sys.exit(1)
  except FileNotFoundError:
    print("Error: Docker is not installed. Please install Docker and try again.")
    print("Visit https://docs.docker.com/get-docker/ for installation instructions.")
    sys.exit(1)

  # Build the Docker image
  try:
    dockerfile_path = os.path.join(
      os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "code", "Dockerfile"
    )
    build_context = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                 "code")
    subprocess.run(
      ["docker", "build", "-t", f"{image_name}:{image_tag}", "-f", dockerfile_path, build_context],
      check=True
    )
  except subprocess.CalledProcessError as e:
    print(f"Error building Docker image: {e}")
    sys.exit(1)

  # Tag the image for ECR
  ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{image_name}:{image_tag}"
  try:
    subprocess.run(["docker", "tag", f"{image_name}:{image_tag}", ecr_repo], check=True)
  except subprocess.CalledProcessError as e:
    print(f"Error tagging Docker image: {e}")
    sys.exit(1)

  # Get ECR login token and login
  ecr = boto3.client("ecr")
  token = ecr.get_authorization_token()
  username, password = base64.b64decode(
    token["authorizationData"][0]["authorizationToken"]).decode().split(":")
  registry = token["authorizationData"][0]["proxyEndpoint"]

  subprocess.run(["docker", "login", "-u", username, "-p", password, registry], check=True)

  # Push the image to ECR
  subprocess.run(["docker", "push", ecr_repo], check=True)

  return ecr_repo


def main():
  # Load environment variables from .env file
  env_path = Path(__file__).parent / ".env"
  if env_path.exists():
    load_dotenv(env_path)
  else:
    print("Warning: .env file not found at", env_path)

  # Parse command line arguments
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument("--debug", action="store_true", help="Enable debug mode")
  parser.add_argument("--build-only", action="store_true", help="Only build and push Docker image")
  args = parser.parse_args()

  # Check AWS environment first
  check_aws_environment()

  if args.debug:
    print("Debug mode enabled")

  # Import helpers

  # Initialize AWS clients
  region = "us-east-2"
  account_id = get_account_id()

  # Get execution role and verify permissions
  role = get_execution_role()
  print(f"Using execution role: {role}")


  # Build and push Docker image
  image_tag = get_user_docker_image_tag()
  user_registry_name = get_user_registry_name()
  ecr_image_uri = build_and_push_docker_image(user_registry_name, account_id, region, image_tag)

  if args.build_only:
    print("Build completed successfully")
    sys.exit(0)

  # Initialize AWS clients
  region = "us-east-2"
  account_id = get_account_id()

  # Get execution role and verify permissions
  role = get_execution_role()
  print(f"Using execution role: {role}")

  # Initialize SageMaker session with user-specific bucket
  sagemaker_session = sagemaker.Session()
  user_bucket_name = get_user_bucket_name()
  sagemaker_session.default_bucket = lambda: user_bucket_name

  # Verify role has required permissions
  iam = boto3.client("iam")
  try:
    iam.simulate_principal_policy(PolicySourceArn=role,
                                  ActionNames=["sagemaker:CreateProcessingJob"])
    print("Role has required SageMaker permissions")
  except Exception as e:
    print(f"Warning: Role may not have required permissions: {e}")

  # Build and push Docker image
  image_tag = get_user_docker_image_tag()
  user_registry_name = get_user_registry_name()
  image_name = f"{user_registry_name}"
  ecr_image_uri = build_and_push_docker_image(image_name, account_id, region, image_tag)

  username = get_user_name()

  # Create SageMaker processor with tags
  processor = ScriptProcessor(
    image_uri=ecr_image_uri,
    command=["python3"],
    role=role,
    instance_count=1,
    instance_type=settings.sagemaker.instance_type,
    volume_size_in_gb=settings.sagemaker.volume_size,
    max_runtime_in_seconds=MAX_RUNTIME_SECONDS,
    sagemaker_session=sagemaker_session,
    tags=[{"Key": "team", "Value": username}],
  )

  # Run the processing job
  processor.run(
    code="sua_outsmarting_outbreaks/pipeline.py",
    inputs=[
      ProcessingInput(
        source=f"s3://{os.environ.get('DATA_BUCKET_NAME', 'sua-outsmarting-outbreaks-challenge-comp')}",
        destination="/opt/ml/processing/input",
      )
    ],
    outputs=[
      ProcessingOutput(
        output_name="output",
        source="/opt/ml/processing/output",
        destination=f"s3://{sagemaker_session.default_bucket()}/output",
      )
    ],
  )


if __name__ == "__main__":
  main()
