import boto3
import os

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
    except:
        # If not running in SageMaker, use the current user/role
        sts = boto3.client('sts')
        caller_identity = sts.get_caller_identity()
        
        # Extract username from caller identity
        arn_parts = caller_identity['Arn'].split('/')
        username = arn_parts[-1] if len(arn_parts) > 1 else 'default'
        
        # Check if current credentials are for a role
        if ':role/' in caller_identity['Arn']:
            return caller_identity['Arn']
            
        # If using user credentials, try to assume SageMaker role
        try:
            role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/SageMakerRole-{username}"
            assumed_role = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName="local-dev-session"
            )
            return role_arn
        except Exception as e:
            print(f"Failed to assume SageMaker role: {e}")
            # If can't assume role, return current user ARN
            return caller_identity['Arn']
