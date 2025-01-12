# Import necessary libraries
import boto3
import pandas as pd
from scipy.spatial import cKDTree

from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger
from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_execution_role,
    get_user_bucket_name,
    get_user_name,
)

# Initialize S3 client and get team bucket
s3_client = boto3.client("s3")

username = get_user_name()
role = get_execution_role()
data_bucket_name = get_data_bucket_name()
user_bucket_name = get_user_bucket_name()

# Define common tags
tags = [{"Key": "team", "Value": username}]

logger.info(f"Using input bucket: {data_bucket_name}")
logger.info(f"Using team bucket: {user_bucket_name}")


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


# Load datasets with error handling
logger.info("Downloading datasets from S3...")
try:
    train = pd.read_csv(f"s3://{data_bucket_name}/Train.csv")
    test = pd.read_csv(f"s3://{data_bucket_name}/Test.csv")
    toilets = pd.read_csv(f"s3://{data_bucket_name}/toilets.csv")
    waste_management = pd.read_csv(f"s3://{data_bucket_name}/waste_management.csv")
    water_sources = pd.read_csv(f"s3://{data_bucket_name}/water_sources.csv")
except FileNotFoundError as e:
    logger.error(f"Error: Required input file not found: {e!s}")
    logger.error(f"Please ensure all required files exist in s3://{data_bucket_name}/")
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
processed_train = merged_data[merged_data["Year"] < TRAIN_CUTOFF_YEAR]
processed_test = merged_data[merged_data["Year"] == TRAIN_CUTOFF_YEAR]

train_output_path = f"s3://{user_bucket_name}/processed_train.csv"
test_output_path = f"s3://{user_bucket_name}/processed_test.csv"

processed_train.to_csv(train_output_path, index=False)
processed_test.to_csv(test_output_path, index=False)

logger.info(f"Processed train dataset saved to {train_output_path}")
logger.info(f"Processed test dataset saved to {test_output_path}")
