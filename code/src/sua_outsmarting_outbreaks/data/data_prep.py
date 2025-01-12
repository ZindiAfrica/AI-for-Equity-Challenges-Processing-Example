"""Data preparation module for preprocessing training and test data."""

import os
from pathlib import Path

import boto3
import pandas as pd
from scipy.spatial import cKDTree

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_execution_role,
    get_user_bucket_name,
    get_user_name,
)
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

def get_data_dir() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent.parent.parent / "data"

def ensure_data_dir() -> Path:
    """Ensure the data directory exists."""
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def download_from_s3(bucket: str, key: str, local_path: Path) -> None:
    """Download a file from S3."""
    if not local_path.exists():
        logger.info(f"Downloading {key} from S3...")
        s3_client = boto3.client("s3")
        s3_client.download_file(bucket, key, str(local_path))

def upload_to_s3(local_path: Path, bucket: str, key: str) -> None:
    """Upload a file to S3."""
    logger.info(f"Uploading to s3://{bucket}/{key}")
    s3_client = boto3.client("s3")
    s3_client.upload_file(str(local_path), bucket, key)

def preprocess_data(local_only: bool = False) -> None:
    """Preprocess the data for training and testing.
    
    Args:
        local_only: If True, only process local files without S3 interaction
    """
    data_dir = ensure_data_dir()
    
    if not local_only:
        # Initialize AWS resources
        s3_client = boto3.client("s3")
        username = get_user_name()
        role = get_execution_role()
        data_bucket_name = get_data_bucket_name()
        user_bucket_name = get_user_bucket_name()
        
        # Define common tags
        tags = [{"Key": "team", "Value": username}]
        
        logger.info(f"Using input bucket: {data_bucket_name}")
        logger.info(f"Using team bucket: {user_bucket_name}")
        
        # Load and process datasets
        train, test, toilets, waste_management, water_sources = load_datasets(data_bucket_name)
        
        # Combine train and test datasets
        hospital_data = pd.concat([train, test])
        
        # Process the data
        merged_data = process_data(hospital_data, toilets, waste_management, water_sources)
        
        # Save results
        save_processed_data(merged_data, user_bucket_name)


# Configure instance type based on data size
# Using ml.m5.2xlarge ($0.46/hr on-demand, $0.138/hr spot) for optimal memory/cost ratio
# - 8 vCPU, 32 GiB RAM
# - Up to 10 Gigabit network
# - 2300 MBps EBS bandwidth


# Helper function to find nearest locations
def find_nearest(
    hospital_df: pd.DataFrame,
    location_df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    id_col: str,
) -> dict[str, str]:
    """Find nearest locations using KD-tree spatial indexing.

    Args:
        hospital_df: DataFrame containing hospital locations
        location_df: DataFrame containing reference locations
        lat_col: Name of latitude column
        lon_col: Name of longitude column
        id_col: Name of ID column

    Returns:
        Dictionary mapping hospital IDs to nearest location IDs

    """
    tree = cKDTree(location_df[[lat_col, lon_col]].values)
    nearest = {}
    for _, row in hospital_df.iterrows():
        _, idx = tree.query([row["Transformed_Latitude"], row["Transformed_Longitude"]])
        nearest[row["ID"]] = location_df.iloc[idx][id_col]
    return nearest


def load_datasets(data_bucket: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all required datasets from S3.
    
    Args:
        data_bucket: S3 bucket containing the data files
        
    Returns:
        Tuple of DataFrames (train, test, toilets, waste_management, water_sources)
    """
    logger.info("Downloading datasets from S3...")
    try:
        train = pd.read_csv(f"s3://{data_bucket}/Train.csv")
        test = pd.read_csv(f"s3://{data_bucket}/Test.csv")
        toilets = pd.read_csv(f"s3://{data_bucket}/toilets.csv")
        waste_management = pd.read_csv(f"s3://{data_bucket}/waste_management.csv")
        water_sources = pd.read_csv(f"s3://{data_bucket}/water_sources.csv")
        return train, test, toilets, waste_management, water_sources
    except FileNotFoundError as e:
        logger.error(f"Error: Required input file not found: {e!s}")
        logger.error(f"Please ensure all required files exist in s3://{data_bucket}/")
        raise
except pd.errors.EmptyDataError:
    logger.error("Error: One or more input files are empty")
    raise
except Exception as e:
    logger.error(f"Error loading input data: {e!s}")
    raise

# Combine train and test datasets
hospital_data = pd.concat([train, test])


# Preprocess water sources
def preprocess_water_sources(water_sources: pd.DataFrame) -> pd.DataFrame:
    """Preprocess water sources data by handling missing values and creating composite keys.

    Args:
        water_sources: DataFrame containing water source information

    Returns:
        DataFrame with preprocessed water source data

    """
    water_sources.dropna(subset=["water_Transformed_Latitude"], inplace=True)
    water_sources["water_Month_Year_lat_lon"] = (
        water_sources["water_Month_Year"]
        + "_"
        + water_sources["water_Transformed_Latitude"].astype(str)
        + "_"
        + water_sources["water_Transformed_Longitude"].astype(str)
    )
    return water_sources


def preprocess_supplementary_data(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Preprocess supplementary datasets by creating composite location-time keys.

    Args:
        df: DataFrame containing supplementary data
        prefix: String prefix for column names (e.g. 'toilet', 'waste')

    Returns:
        DataFrame with added composite key column

    """
    df[f"{prefix}_Month_Year_lat_lon"] = (
        df[f"{prefix}_Month_Year"]
        + "_"
        + df[f"{prefix}_Transformed_Latitude"].astype(str)
        + "_"
        + df[f"{prefix}_Transformed_Longitude"].astype(str)
    )
    return df


water_sources = preprocess_water_sources(water_sources)
toilets = preprocess_supplementary_data(toilets, "toilet")
waste_management = preprocess_supplementary_data(waste_management, "waste")

# Merge datasets with nearest locations
merged_data = hospital_data.copy()
datasets = [
    (toilets, "toilet", "toilet_Month_Year_lat_lon"),
    (waste_management, "waste", "waste_Month_Year_lat_lon"),
    (water_sources, "water", "water_Month_Year_lat_lon"),
]

for df, prefix, id_col in datasets:
    nearest = find_nearest(
        merged_data,
        df,
        f"{prefix}_Transformed_Latitude",
        f"{prefix}_Transformed_Longitude",
        id_col,
    )
    nearest_df = pd.DataFrame(list(nearest.items()), columns=["ID", id_col])
    merged_data = merged_data.merge(nearest_df, on="ID").merge(df, on=id_col)

# Save processed datasets to S3
logger.info("Uploading processed datasets to S3...")
TRAIN_CUTOFF_YEAR = 2023
def save_processed_data(merged_data: pd.DataFrame, user_bucket: str) -> None:
    """Save processed train and test datasets to S3.
    
    Args:
        merged_data: DataFrame containing processed data
        user_bucket: S3 bucket to save results
    """
    processed_train = merged_data[merged_data["Year"] < TRAIN_CUTOFF_YEAR]
    processed_test = merged_data[merged_data["Year"] == TRAIN_CUTOFF_YEAR]

    train_output_path = f"s3://{user_bucket}/processed_train.csv"
    test_output_path = f"s3://{user_bucket}/processed_test.csv"

    logger.info(f"Saving processed train dataset to {train_output_path}")
    processed_train.to_csv(train_output_path, index=False)
    
    logger.info(f"Saving processed test dataset to {test_output_path}")
    processed_test.to_csv(test_output_path, index=False)

logger.info(f"Processed train dataset saved to {train_output_path}")
logger.info(f"Processed test dataset saved to {test_output_path}")
