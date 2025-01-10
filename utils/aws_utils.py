import boto3


def get_execution_role():
    """
    Get the appropriate execution role or user ARN based on the environment.

    Returns:
        str: The ARN to use for AWS operations
    """
    try:
        # Try to get SageMaker execution role
        import sagemaker

        return sagemaker.get_execution_role()
    except Exception:
        # If not running in SageMaker, use the current user/role
        sts = boto3.client("sts")
        caller_identity = sts.get_caller_identity()

        # Extract username from caller identity
        arn_parts = caller_identity["Arn"].split("/")
        username = arn_parts[-1] if len(arn_parts) > 1 else "default"

        # Check if current credentials are for a role
        if ":role/" in caller_identity["Arn"]:
            return caller_identity["Arn"]

        # Only try to assume SageMaker role for comp-user prefixed users
        if username.startswith("comp-user"):
            try:
                role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/SageMakerRole-{username}"
                assumed_role = sts.assume_role(RoleArn=role_arn, RoleSessionName="local-dev-session")
                # Use the temporary credentials from assumed role
                return assumed_role["Credentials"]["AccessKeyId"]
            except Exception as e:
                print(f"Failed to assume SageMaker role: {e}")

        # For non comp-user users or if role assumption fails, return current user ARN
        return caller_identity["Arn"]
