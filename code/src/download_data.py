"""Script for downloading training data from S3."""

import sys
from pathlib import Path

import boto3

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
)
from sua_outsmarting_outbreaks.utils.directory_utils import ensure_dir, get_relative_to_project
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


def download_data(output_dir: str) -> None:
    """Download training data from S3 to local directory.

    Args:
    ----
        output_dir: Local directory to save files

    """
    output_path = ensure_dir(get_relative_to_project(output_dir))

    logger.info(f"Downloading data to {output_path}")

    s3_client = boto3.client("s3")
    data_bucket = get_data_bucket_name()

    # List and download all files from data bucket
    logger.info(f"Listing files in {data_bucket}...")
    data_files = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=data_bucket):
        if "Contents" in page:
            data_files.extend(obj["Key"] for obj in page["Contents"])

    for filename in data_files:
        logger.info(f"Downloading {filename} from data bucket...")
        try:
            # Create subdirectories if needed
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            s3_client.download_file(data_bucket, filename, str(file_path))
        except (OSError, boto3.exceptions.Boto3Error) as e:
            logger.warning(f"Could not download {filename}: {e}")

    logger.info(f"All files downloaded to {output_path}")


if __name__ == "__main__":
    logger.warning("Please use run.sh to download data:")
    logger.warning("  ./run.sh download        # Download training data")
    sys.exit(1)
