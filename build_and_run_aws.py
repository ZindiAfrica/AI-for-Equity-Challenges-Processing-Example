import base64
import os
import subprocess

import boto3
import sagemaker
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor


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
        print(f"AWS_SECRET_ACCESS_KEY: {'*****' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'not set'}")

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


def build_and_push_docker_image(image_name, account_id, region):
    # Build the Docker image
    subprocess.run(["docker", "build", "-t", image_name, "."], check=True)

    # Tag the image for ECR
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{image_name}"
    subprocess.run(["docker", "tag", f"{image_name}:latest", f"{ecr_repo}:latest"], check=True)

    # Get ECR login token and login
    ecr = boto3.client("ecr")
    token = ecr.get_authorization_token()
    username, password = base64.b64decode(token["authorizationData"][0]["authorizationToken"]).decode().split(":")
    registry = token["authorizationData"][0]["proxyEndpoint"]

    subprocess.run(["docker", "login", "-u", username, "-p", password, registry], check=True)

    # Push the image to ECR
    subprocess.run(["docker", "push", f"{ecr_repo}:latest"], check=True)

    return ecr_repo


def main():
    # Check AWS environment first
    check_aws_environment()

    # Import helper
    from utils.aws_utils import get_execution_role

    # Initialize AWS clients
    region = "us-east-2"
    account_id = get_account_id()
    sagemaker_session = sagemaker.Session()
    role = get_execution_role()

    # Import helper
    from utils.aws_utils import get_workspace_name
    
    # Build and push Docker image
    image_name = "outsmarting-pipeline"
    workspace = get_workspace_name()
    ecr_image_uri = build_and_push_docker_image(workspace, account_id, region)

    # Create SageMaker processor
    processor = ScriptProcessor(
        image_uri=ecr_image_uri,
        command=["python3"],
        role=role,
        instance_count=1,
        instance_type="ml.g4dn.8xlarge",
        volume_size_in_gb=100,
        max_runtime_in_seconds=86400,  # 24 hours
        sagemaker_session=sagemaker_session,
    )

    # Run the processing job
    processor.run(
        code="notebooks/outsmarting_sagemaker_execute.py",
        inputs=[
            ProcessingInput(
                source="s3://sua-outsmarting-outbreaks-challenge-comp",
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
