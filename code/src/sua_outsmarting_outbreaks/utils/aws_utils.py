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
    print("\nAttempting to get execution role...")
    try:
        # Try to get SageMaker execution role
        import sagemaker

        role = sagemaker.get_execution_role()
        print(f"Successfully got SageMaker execution role: {role}")
        return role
    except Exception as e:
        print(f"Failed to get SageMaker role: {e}")
        print("Falling back to current user/role credentials...")

        # If not running in SageMaker, use the current user/role
        sts = boto3.client("sts")
        caller_identity = sts.get_caller_identity()
        print(f"Current caller identity: {caller_identity['Arn']}")

        # Extract the full path after user/ or role/
        arn = caller_identity["Arn"]
        if "user/" in arn:
            path_parts = arn.split("user/")[1].split("/")
        elif "role/" in arn:
            path_parts = arn.split("role/")[1].split("/")
        else:
            path_parts = []

        username = path_parts[0] if path_parts else "default"

        print(f"Got username {username}")

        # Check if current credentials are for a role
        if ":role/" in arn:
            print(f"It's a role, returning the ARN: {arn}")
            return arn

        # Try to assume SageMaker role for comp-user pattern
        if "comp-user-" in username:
            try:
                print(f"Matching comp-user pattern: {username}")
                # Extract the comp-user ID portion
                user_id = username.split("comp-user-")[1]
                role_name = f"SageMakerRole-comp-user-{user_id}"
                role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/{role_name}"
                print(f"Attempting to assume role: {role_arn}")

                # Attempt to assume role with longer session duration
                sts.assume_role(
                    RoleArn=role_arn,
                    RoleSessionName="sagemaker-execution-session",
                    DurationSeconds=3600,  # 1 hour session
                )

                # Use the temporary credentials
                print("Successfully assumed SageMaker execution role")
                return role_arn
            except Exception as e:
                print(f"Failed to assume SageMaker role, falling back to user credentials: {e}")
                return caller_identity["Arn"]  # Fall back to user ARN

        # For non comp-user users, return current user ARN
        return caller_identity["Arn"]
