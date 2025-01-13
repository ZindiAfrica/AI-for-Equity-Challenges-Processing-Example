"""AWS utility functions for SageMaker pipeline management."""

import os
from pathlib import Path

import boto3
import botocore

from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)


def get_user_name() -> str:
    """Get the username for the current user.

    Returns:
        str: The username from AWS identity or environment variable.

    Example:
        >>> get_user_name()
        'john-doe'

    """
    sts = boto3.client("sts")
    caller_identity: dict[str, str] = sts.get_caller_identity()
    arn_parts: list[str] = caller_identity["Arn"].split("/")
    username: str = arn_parts[-1] if len(arn_parts) > 1 else "default"
    return os.environ.get("USER_NAME", username)

def initialize_aws_resources() -> tuple[str, str, str, str, list[dict[str, str]]]:
    """Initialize common AWS resources and return configuration.

    Returns:
        Tuple containing:
            str: Username
            str: IAM role ARN
            str: Data bucket name
            str: User bucket name
            list: Common tags

    """
    username = get_user_name()
    role = get_execution_role()
    data_bucket_name = get_data_bucket_name()
    user_bucket_name = get_user_bucket_name()

    # Define common tags
    tags = get_tags()

    return username, role, data_bucket_name, user_bucket_name, tags


def get_tags(additional_tags: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
  """Get common tags for AWS resources, merging with additional tags if provided.

  Args:
      additional_tags (list, optional): Additional tags to merge with default tags.

  Returns:
      list: Merged list of unique tags for AWS resources.

  Example:
      >>> get_tags([{"Key": "project", "Value": "outbreak"}])
      [{'Key': 'team', 'Value': 'john-doe'}, {'Key': 'project', 'Value': 'outbreak'}]

  """
  default_tags = [{"Key": "team", "Value": get_user_name()}]
  tag_dict = {tag["Key"]: tag["Value"] for tag in default_tags}

  if additional_tags:
    for tag in additional_tags:
      tag_dict[tag["Key"]] = tag["Value"]

  return [{"Key": key, "Value": value} for key, value in tag_dict.items()]


def get_user_registry_name() -> str:
    """Get the ECR registry name for the current user.

    Returns:
        str: The ECR registry name, formatted as '{username}-workspace'.

    Example:
        >>> get_user_registry_name()
        'john-doe-workspace'

    """
    username: str = get_user_name()
    return os.environ.get("USER_REGISTRY_NAME", f"{username}-workspace")


def get_user_bucket_name() -> str:
    """Get the S3 bucket name for the current user.

    Returns:
        str: The S3 bucket name, formatted as '{username}-team-bucket'.

    Example:
        >>> get_user_bucket_name()
        'john-doe-team-bucket'

    """
    username: str = get_user_name()
    return os.environ.get("USER_BUCKET_NAME", f"{username}-team-bucket")


def get_data_bucket_name() -> str:
    """Get the source data bucket name.

    Returns:
        str: The S3 bucket name containing source data.

    Example:
        >>> get_data_bucket_name()
        'sua-outsmarting-outbreaks-challenge-comp'

    """
    return os.environ.get("DATA_BUCKET_NAME", "sua-outsmarting-outbreaks-challenge-comp")

def get_data_source(local_data_dir: str | None = None) -> tuple[str, bool]:
    """Get the data source location and type.
    
    Args:
        local_data_dir: Optional local directory path for data
        
    Returns:
        Tuple of (path, is_local) where path is either local path or S3 URI

    """
    if local_data_dir:
        return str(Path(local_data_dir).resolve()), True
    return f"s3://{get_data_bucket_name()}/", False


def get_user_docker_image_tag() -> str:
    """Get the Docker image tag for the current user.

    Returns:
        str: The Docker image tag to use for builds.

    Example:
        >>> get_user_docker_image_tag()
        'outsmarting-pipeline'

    """
    return os.environ.get("DOCKER_IMAGE_TAG", "outsmarting-pipeline")


def get_script_processor_type() -> str:
    """Get the SageMaker script processor instance type.

    Returns:
        str: The SageMaker instance type (e.g. 'ml.m5.2xlarge').

    Example:
        >>> get_script_processor_type()
        'ml.m5.2xlarge'

    """
    return os.environ.get("SCRIPT_PROCESSOR_TYPE", "ml.m5.2xlarge")


def get_execution_role() -> str:
    """Get the appropriate execution role or user ARN based on the environment.

    This function attempts to get the SageMaker execution role first, then falls back
    to the current user/role credentials if not running in SageMaker.

    Returns:
        str: The ARN to use for AWS operations.

    Raises:
        Exception: If unable to get valid credentials.

    Example:
        >>> get_execution_role()
        'arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole'

    """
    logger.info("Attempting to get execution role...")
    try:
        # Try to get SageMaker execution role
        import sagemaker

        role = sagemaker.get_execution_role()
        logger.info(f"Successfully got SageMaker execution role: {role}")
        return role
    except (botocore.exceptions.ClientError, ValueError) as e:
        logger.error(f"Failed to get SageMaker role: {e}")
        logger.info("Falling back to current user/role credentials...")

        # If not running in SageMaker, use the current user/role
        sts = boto3.client("sts")
        caller_identity = sts.get_caller_identity()
        logger.info(f"Current caller identity: {caller_identity['Arn']}")

        # Extract the full path after user/ or role/
        arn = caller_identity["Arn"]
        if "user/" in arn:
            path_parts = arn.split("user/")[1].split("/")
        elif "role/" in arn:
            path_parts = arn.split("role/")[1].split("/")
        else:
            path_parts = []

        username = path_parts[0] if path_parts else "default"

        logger.info(f"Got username {username}")

        # Check if current credentials are for a role
        if ":role/" in arn:
            logger.info(f"It's a role, returning the ARN: {arn}")
            return arn

        # Try to assume SageMaker role for comp-user pattern
        if "comp-user-" in username:
            try:
                logger.info(f"Matching comp-user pattern: {username}")
                # Extract the comp-user ID portion
                role_name = f"SageMakerRole-{username}"
                role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/{role_name}"
                logger.info(f"Attempting to assume role: {role_arn}")

                # Attempt to assume role with longer session duration
                sts.assume_role(
                    RoleArn=role_arn,
                    RoleSessionName="sagemaker-execution-session",
                    DurationSeconds=3600,  # 1 hour session
                )

                # Use the temporary credentials
                logger.info("Successfully assumed SageMaker execution role")
                return role_arn
            except botocore.exceptions.ClientError as e:
                logger.error(f"Failed to assume SageMaker role, falling back to user credentials: {e}")
                return caller_identity["Arn"]  # Fall back to user ARN

        # For non comp-user users, return current user ARN
        return caller_identity["Arn"]
