"""Script for downloading training data from S3."""

import logging
from pathlib import Path

import boto3
import click

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_user_bucket_name,
)
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def download_data(output_dir: str) -> None:
    """Download training data from S3 to local directory.
    
    Args:
        output_dir: Local directory to save files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    s3_client = boto3.client('s3')
    data_bucket = get_data_bucket_name()
    user_bucket = get_user_bucket_name()

    # List and download all files from data bucket
    logger.info(f"Listing files in {data_bucket}...")
    data_files = []
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=data_bucket):
        if 'Contents' in page:
            data_files.extend(obj['Key'] for obj in page['Contents'])
    
    for filename in data_files:
        logger.info(f"Downloading {filename} from data bucket...")
        try:
            s3_client.download_file(
                data_bucket,
                filename,
                str(output_path / filename)
            )
        except Exception as e:
            logger.warning(f"Could not download {filename}: {e}")

    # List and download all files from user bucket
    logger.info(f"Listing files in {user_bucket}...")
    user_files = []
    for page in paginator.paginate(Bucket=user_bucket):
        if 'Contents' in page:
            user_files.extend(obj['Key'] for obj in page['Contents'])
    
    for filename in user_files:
        logger.info(f"Downloading {filename} from user bucket...")
        try:
            # Create subdirectories if needed
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            s3_client.download_file(
                user_bucket,
                filename,
                str(file_path)
            )
        except Exception as e:
            logger.warning(f"Could not download {filename}: {e}")

    logger.info(f"All files downloaded to {output_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Download training data from S3")
    parser.add_argument("output_dir", help="Directory to save downloaded files")
    args = parser.parse_args()
    
    try:
        download_data(args.output_dir)
    except Exception as e:
        logger.error(f"Failed to download data: {e}")
        raise
