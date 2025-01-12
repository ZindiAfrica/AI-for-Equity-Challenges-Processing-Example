import base64
import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import boto3
import botocore
import sagemaker
from dotenv import load_dotenv
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_execution_role,
    get_user_bucket_name,
    get_user_docker_image_tag,
    get_user_name,
    get_user_registry_name,
)
from sua_outsmarting_outbreaks.utils.config import settings
from sua_outsmarting_outbreaks.utils.constants import MAX_RUNTIME_SECONDS
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

# Suppress specific pydantic warning
warnings.filterwarnings(
    "ignore",
    message='Field name "json" in "MonitoringDatasetFormat" shadows an attribute in parent "Base"',
)

try:
    import boto3
    import sagemaker
except ImportError:
    logger.error("Required packages are missing. Please install them with:")
    logger.error("pip install boto3 sagemaker")
    sys.exit(1)


def check_aws_environment() -> None:
    """Print AWS environment settings and handle AWS_PROFILE precedence."""
    aws_profile = os.environ.get("AWS_PROFILE", "")

    if aws_profile:
        logger.info(f"Using AWS_PROFILE: {aws_profile}")
        # If AWS_PROFILE is set, unset other AWS environment variables
        for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]:
            if key in os.environ:
                del os.environ[key]
    else:
        # Print individual credentials if AWS_PROFILE is not set
        logger.info(f"AWS_ACCESS_KEY_ID: {'*****' if os.environ.get('AWS_ACCESS_KEY_ID') else 'not set'}")
        logger.info(f"AWS_REGION: {os.environ.get('AWS_REGION', 'not set')}")
        logger.info(f"AWS_SECRET_ACCESS_KEY: {'*****' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'not set'}")

    # Get and print current user identity
    try:
        sts = boto3.client("sts")
        caller_identity = sts.get_caller_identity()
        username = caller_identity["Arn"].split("/")[-1]
        logger.info(f"AWS Username: {username}")
    except (boto3.exceptions.Boto3Error, boto3.exceptions.BotoCoreError) as e:
        logger.error(f"Failed to get AWS identity: {e}")


def get_docker_executable() -> str:
    """Get the full path to the docker executable.

    Returns:
        str: Full path to docker executable

    Raises:
        RuntimeError: If docker executable is not found

    """
    docker_path = shutil.which("docker")
    if not docker_path:
        raise RuntimeError("Docker executable not found in PATH")
    return docker_path


def validate_docker_args(*args: str) -> None:
    """Validate docker command arguments.
    
    Args:
        *args: Docker command arguments to validate
        
    Raises:
        ValueError: If any argument contains invalid characters

    """
    # Define allowed patterns for different arg types
    import re
    tag_pattern = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")
    path_pattern = re.compile(r"^[a-zA-Z0-9/._-]+$")

    for arg in args:
        if not isinstance(arg, str):
            raise ValueError(f"Invalid argument type: {type(arg)}")
        if "\x00" in arg or ";" in arg or "|" in arg:
            raise ValueError(f"Invalid characters in argument: {arg}")
        if arg.startswith("-") and arg not in ["-t", "-f", "-u", "-p"]:
            raise ValueError(f"Invalid flag argument: {arg}")
        if ":" in arg and not tag_pattern.match(arg.split(":")[1]):
            raise ValueError(f"Invalid image tag format: {arg}")
        if "/" in arg and not path_pattern.match(arg):
            raise ValueError(f"Invalid path format: {arg}")


def get_account_id() -> str:
    """Get the AWS account ID for the current session.

    Returns:
        str: The AWS account ID

    """
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def build_and_push_docker_image(
    image_name: str,
    account_id: str,
    region: str,
    image_tag: str,
) -> str:
    """Build and push Docker image to ECR.

    Args:
        image_name: Name of the Docker image
        account_id: AWS account ID
        region: AWS region
        image_tag: Tag for the Docker image

    Returns:
        str: The full ECR repository URI for the pushed image

    """
    # Get validated docker executable path
    docker_exe = get_docker_executable()

    # Check if Docker daemon is running
    try:
        validate_docker_args("info")
        subprocess.run([docker_exe, "info"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.error("Docker daemon is not running. Please start Docker and try again.")
        logger.error("On macOS, launch Docker Desktop from Applications.")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid docker command: {e}")
        sys.exit(1)

    # Build the Docker image
    try:
        dockerfile_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "code",
            "Dockerfile",
        )
        build_context = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "code")

        validate_docker_args("build", "-t", f"{image_name}:{image_tag}", "-f", dockerfile_path, build_context)
        subprocess.run(
            [docker_exe, "build", "-t", f"{image_name}:{image_tag}", "-f", dockerfile_path, build_context],
            check=True,
        )
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Error building Docker image: {e}")
        sys.exit(1)

    # Tag the image for ECR
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{image_name}:{image_tag}"
    try:
        validate_docker_args("tag", f"{image_name}:{image_tag}", ecr_repo)
        subprocess.run([docker_exe, "tag", f"{image_name}:{image_tag}", ecr_repo], check=True)
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Error tagging Docker image: {e}")
        sys.exit(1)

    # Get ECR login token and login
    ecr = boto3.client("ecr")
    token = ecr.get_authorization_token()
    username, password = base64.b64decode(token["authorizationData"][0]["authorizationToken"]).decode().split(":")
    registry = token["authorizationData"][0]["proxyEndpoint"]

    try:
        validate_docker_args("login", "-u", username, "-p", password, registry)
        subprocess.run([docker_exe, "login", "-u", username, "-p", password, registry], check=True)
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Error logging into ECR: {e}")
        sys.exit(1)

    # Push the image to ECR
    try:
        validate_docker_args("push", ecr_repo)
        subprocess.run([docker_exe, "push", ecr_repo], check=True)
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Error pushing image to ECR: {e}")
        sys.exit(1)

    return ecr_repo


def main() -> None:
    """Execute the main AWS pipeline build and run process."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        logger.warning(f"Warning: .env file not found at {env_path}")

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--build-only", action="store_true", help="Only build and push Docker image")
    args = parser.parse_args()

    # Check AWS environment first
    check_aws_environment()

    if args.debug:
        logger.info("Debug mode enabled")

    # Import helpers

    # Initialize AWS clients
    region = "us-east-2"
    account_id = get_account_id()

    # Get execution role and verify permissions
    role = get_execution_role()
    logger.info(f"Using execution role: {role}")

    # Build and push Docker image
    image_tag = get_user_docker_image_tag()
    user_registry_name = get_user_registry_name()
    ecr_image_uri = build_and_push_docker_image(user_registry_name, account_id, region, image_tag)

    if args.build_only:
        logger.info("Build completed successfully")
        sys.exit(0)

    # Initialize AWS clients
    region = "us-east-2"
    account_id = get_account_id()

    # Get execution role and verify permissions
    role = get_execution_role()
    logger.info(f"Using execution role: {role}")

    # Initialize SageMaker session with user-specific bucket
    sagemaker_session = sagemaker.Session()
    user_bucket_name = get_user_bucket_name()
    sagemaker_session.default_bucket = lambda: user_bucket_name

    # Verify role has required permissions
    iam = boto3.client("iam")
    try:
        iam.simulate_principal_policy(PolicySourceArn=role, ActionNames=["sagemaker:CreateProcessingJob"])
        logger.info("Role has required SageMaker permissions")
    except (boto3.exceptions.BotoCoreError, boto3.exceptions.ClientError) as e:
        logger.warning(f"Role may not have required permissions: {e}")

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
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="output",
                source="/opt/ml/processing/output",
                destination=f"s3://{sagemaker_session.default_bucket()}/output",
            ),
        ],
    )


if __name__ == "__main__":
    main()
