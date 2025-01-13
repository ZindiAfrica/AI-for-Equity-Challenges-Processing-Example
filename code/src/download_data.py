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

    # Download raw data files
    raw_files = ['Train.csv', 'Test.csv', 'toilets.csv', 'waste_management.csv', 'water_sources.csv']
    for filename in raw_files:
        logger.info(f"Downloading {filename}...")
        s3_client.download_file(
            data_bucket,
            filename,
            str(output_path / filename)
        )

    # Download processed files if they exist
    processed_files = ['processed_train.csv', 'processed_test.csv']
    for filename in processed_files:
        try:
            logger.info(f"Downloading {filename}...")
            s3_client.download_file(
                user_bucket,
                filename,
                str(output_path / filename)
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
