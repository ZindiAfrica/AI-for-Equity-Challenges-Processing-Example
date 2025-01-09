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
        
        # Check if current credentials are for a role
        if ':role/' in caller_identity['Arn']:
            return caller_identity['Arn']
            
        # If using user credentials, try to assume SageMaker execution role
        try:
            role_arn = f"arn:aws:iam::{caller_identity['Account']}:role/service-role/AmazonSageMaker-ExecutionRole"
            assumed_role = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName="local-dev-session"
            )
            return role_arn
        except:
            # If can't assume role, return current user ARN
            return caller_identity['Arn']
