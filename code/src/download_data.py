"""Script for downloading training data from S3."""

from pathlib import Path

import boto3

from sua_outsmarting_outbreaks.data.data_prep import get_data_dir
from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
)
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def download_data(output_dir: str) -> None:
    """Download training data from S3 to local directory.

    Args:
        output_dir: Local directory to save files

    """
    # Get the project root directory (3 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    # Convert output_dir to absolute path relative to project root
    output_path = (project_root / output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

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

            s3_client.download_file(
                data_bucket,
                filename,
                str(file_path)
            )
        except (boto3.exceptions.Boto3Error, IOError) as e:
            logger.warning(f"Could not download {filename}: {e}")

    logger.info(f"All files downloaded to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download training data from S3")
    parser.add_argument("--output-dir", help="Directory to save downloaded files", default=None)
    args = parser.parse_args()

    try:
        output_dir = args.output_dir if args.output_dir else str(get_data_dir())
        download_data(output_dir)
    except Exception as e:
        logger.error(f"Failed to download data: {e}")
        raise
