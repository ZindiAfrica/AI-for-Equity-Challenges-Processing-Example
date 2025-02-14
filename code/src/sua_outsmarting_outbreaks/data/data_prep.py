"""Data preparation module for preprocessing training and test data."""

from pathlib import Path

import boto3
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_data_source,
    get_user_bucket_name,
)
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

from sua_outsmarting_outbreaks.utils.directory_utils import get_data_dir, ensure_dir

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

def preprocess_data(local_data_dir: str | None = None, output_dir: str | None = None) -> None:
    """Preprocess the data for training and testing.

    Args:
        local_data_dir: Optional local directory containing input data files
        output_dir: Optional local directory for output files

    """
    data_path, is_local = get_data_source(local_data_dir)

    # Initialize AWS resources
    data_bucket_name = get_data_bucket_name()
    user_bucket_name = get_user_bucket_name()

    logger.info(f"Using input bucket: {data_bucket_name}")
    logger.info(f"Using team bucket: {user_bucket_name}")

    # Load datasets from either local or S3
    if is_local:
        data_path = Path(data_path).resolve()
        logger.info(f"Loading data from local directory: {data_path}")
        logger.debug(f"Directory contents: {list(data_path.glob('*.csv'))}")

        try:
            train_path = data_path / "Train.csv"
            test_path = data_path / "Test.csv"
            toilets_path = data_path / "toilets.csv"
            waste_path = data_path / "waste_management.csv"
            water_path = data_path / "water_sources.csv"

            # Check if files exist
            for p in [train_path, test_path, toilets_path, waste_path, water_path]:
                if not p.exists():
                    raise FileNotFoundError(f"Required file not found: {p}")

            logger.debug(f"Attempting to read files from: {data_path}")
            logger.debug(f"Directory contents: {list(data_path.glob('*.csv'))}")

            train = pd.read_csv(train_path)
            logger.debug(f"Train path: {train_path}")
            logger.debug(f"Train columns: {train.columns.tolist()}")
            logger.debug(f"Train head:\n{train.head()}")

            test = pd.read_csv(test_path)
            logger.debug(f"Test path: {test_path}")
            logger.debug(f"Test columns: {test.columns.tolist()}")
            logger.debug(f"Test head:\n{test.head()}")

            toilets = pd.read_csv(toilets_path)
            logger.debug(f"Toilets path: {toilets_path}")
            logger.debug(f"Toilets columns: {toilets.columns.tolist()}")
            logger.debug(f"Toilets head:\n{toilets.head()}")

            waste_management = pd.read_csv(waste_path)
            logger.debug(f"Waste management path: {waste_path}")
            logger.debug(f"Waste management columns: {waste_management.columns.tolist()}")
            logger.debug(f"Waste management head:\n{waste_management.head()}")

            water_sources = pd.read_csv(water_path)
            logger.debug(f"Water sources path: {water_path}")
            logger.debug(f"Water sources columns: {water_sources.columns.tolist()}")
            logger.debug(f"Water sources head:\n{water_sources.head()}")

            logger.info(f"Loaded training data shape: {train.shape}")
            logger.info(f"Loaded test data shape: {test.shape}")
            logger.debug(f"Train contents: {train}")
            # Fill missing values in target column
            train["Total"] = train["Total"].fillna(0)
            test["Total"] = test["Total"].fillna(0)

        except FileNotFoundError as e:
            logger.error(f"Could not find required data file: {e}")
            raise
        except pd.errors.EmptyDataError:
            logger.error("One or more data files are empty")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    else:
        # Load from S3 data bucket
        train, test, toilets, waste_management, water_sources = load_datasets(data_bucket_name)

    # Combine train and test datasets
    hospital_data = pd.concat([train, test])

    # Process the data
    merged_data = process_data(hospital_data, toilets, waste_management, water_sources)

    # Save results to user bucket or local dir
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving processed data to {output_path}")
        processed_train = merged_data[merged_data["Year"] < TRAIN_CUTOFF_YEAR]
        processed_test = merged_data[merged_data["Year"] == TRAIN_CUTOFF_YEAR]
        processed_train.to_csv(output_path / "processed_train.csv", index=False)
        processed_test.to_csv(output_path / "processed_test.csv", index=False)
    else:
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
    location_df = location_df[np.isfinite(location_df[[lat_col, lon_col]]).all(axis=1)]
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


def process_data(hospital_data: pd.DataFrame, toilets_df: pd.DataFrame, waste_df: pd.DataFrame, water_df: pd.DataFrame) -> pd.DataFrame:
    """Process and merge all datasets.

    Args:
        hospital_data: DataFrame with hospital data
        toilets_df: DataFrame with toilet data
        waste_df: DataFrame with waste management data
        water_df: DataFrame with water source data

    Returns:
        DataFrame with all data merged

    """
    # Preprocess each dataset
    water_sources = preprocess_water_sources(water_df)
    toilets = preprocess_supplementary_data(toilets_df, "toilet")
    waste_management = preprocess_supplementary_data(waste_df, "waste")

    # Merge datasets with nearest locations
    merged_data = hospital_data.copy()
    datasets = [
        (toilets, "toilet", "toilet_Month_Year_lat_lon"),
        (waste_management, "waste", "waste_Month_Year_lat_lon"),
        (water_sources, "water", "water_Month_Year_lat_lon"),
    ]

    # Process and merge each dataset
    for df, prefix, id_col in [
        (toilets, "toilet", "toilet_Month_Year_lat_lon"),
        (waste_management, "waste", "waste_Month_Year_lat_lon"),
        (water_sources, "water", "water_Month_Year_lat_lon"),
    ]:
        nearest = find_nearest(
            hospital_data,
            df,
            f"{prefix}_Transformed_Latitude",
            f"{prefix}_Transformed_Longitude",
            id_col,
        )
        nearest_df = pd.DataFrame(list(nearest.items()), columns=["ID", id_col])
        hospital_data = hospital_data.merge(nearest_df, on="ID").merge(df, on=id_col)

    return hospital_data

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

