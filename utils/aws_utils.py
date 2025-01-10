import boto3


def get_workspace_name():
    """Get the workspace name for the current user"""
    sts = boto3.client("sts")
    caller_identity = sts.get_caller_identity()
    arn_parts = caller_identity["Arn"].split("/")
    username = arn_parts[-1] if len(arn_parts) > 1 else "default"
    return f"{username}-workspace"


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

        # Try to assume SageMaker role for comp-user prefixed users
        if username.startswith("comp-user"):
            try:
                # Construct role name with SageMakerRole- prefix
                role_name = f"SageMakerRole-{username}"
                role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/{role_name}"
                assumed_role = sts.assume_role(RoleArn=role_arn, RoleSessionName="local-dev-session")
                return role_arn  # Return the role ARN instead of temporary credentials
            except Exception as e:
                print(f"Failed to assume SageMaker role, falling back to user credentials: {e}")
                return caller_identity["Arn"]  # Fall back to user ARN

        # For non comp-user users, return current user ARN
        return caller_identity["Arn"]
