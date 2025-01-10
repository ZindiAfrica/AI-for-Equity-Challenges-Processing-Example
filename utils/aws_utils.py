import boto3


def get_user_name():
    """Get the workspace name for the current user"""
    sts = boto3.client("sts")
    caller_identity = sts.get_caller_identity()
    arn_parts = caller_identity["Arn"].split("/")
    username = arn_parts[-1] if len(arn_parts) > 1 else "default"
    return username


def get_registry_name():
    """Get the workspace name for the current user"""
    username = get_user_name()
    return f"{username}-workspace"


def get_bucket_name():
    """Get the workspace name for the current user"""
    username = get_user_name()
    return f"{username}-team-bucket"


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

        # Extract the full path after user/ or role/
        arn = caller_identity["Arn"]
        if "/user/" in arn:
            path_parts = arn.split("/user/")[1].split("/")
        elif "/role/" in arn:
            path_parts = arn.split("/role/")[1].split("/")
        else:
            path_parts = []
        
        username = path_parts[0] if path_parts else "default"

        # Check if current credentials are for a role
        if ":role/" in arn:
            return arn

        # Try to assume SageMaker role for comp-user pattern
        if "comp-user-" in username:
            try:
                # Extract the comp-user ID portion
                user_id = username.split("comp-user-")[1]
                role_name = f"SageMakerRole-comp-user-{user_id}"
                role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/{role_name}"
                # Attempt to assume role to verify access
                sts.assume_role(RoleArn=role_arn, RoleSessionName="local-dev-session")
                return role_arn  # Return the role ARN instead of temporary credentials
            except Exception as e:
                print(f"Failed to assume SageMaker role, falling back to user credentials: {e}")
                return caller_identity["Arn"]  # Fall back to user ARN

        # For non comp-user users, return current user ARN
        return caller_identity["Arn"]
