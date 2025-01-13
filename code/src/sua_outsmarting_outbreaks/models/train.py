"""Model training module for the SUA Outsmarting Outbreaks Challenge.

This module handles the training of a RandomForest regression model using preprocessed data.
It includes data loading, feature engineering, model training and model artifact storage.

Example:
    This script is typically run as part of the SageMaker processing job:
    >>> python -m sua_outsmarting_outbreaks.models.train

"""

import boto3
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sua_outsmarting_outbreaks.utils.aws_utils import (
    initialize_aws_resources,
    get_script_processor_type,
)
from sua_outsmarting_outbreaks.utils.constants import INSTANCE_SPECS
from sua_outsmarting_outbreaks.utils.logging_utils import (
    DataError,
    ModelError,
    setup_logger,
)

# Configure logger
logger = setup_logger(__name__)

# Initialize AWS resources
s3_client = boto3.client("s3")
username, role, data_bucket_name, user_bucket_name, tags = initialize_aws_resources()

instance_type = get_script_processor_type()
instance_specs = INSTANCE_SPECS.get(instance_type)

logger.info(f"Using team bucket: {user_bucket_name}")
logger.info("Using instance specifications:")
logger.info(f"- Instance type: {instance_type}")
if instance_specs:
    logger.info(f"- GPU: {instance_specs['gpu']}")
    logger.info(f"- CPU/RAM: {instance_specs['cpu_ram']}")
    logger.info(f"- Network: {instance_specs['network']}")
    logger.info(f"- Storage: {instance_specs['storage']}")
    logger.info(f"- Cost: ${instance_specs['cost']['on_demand']}/hr (on-demand) or ${instance_specs['cost']['spot']}/hr (spot)")
else:
    logger.warning(f"No specifications found for instance type: {instance_type}")


def load_training_data(bucket_name: str) -> pd.DataFrame:
    """Load preprocessed training data from S3.

    Args:
        bucket_name: Name of the S3 bucket containing the data

    Returns:
        DataFrame containing the training data

    Raises:
        DataError: If there are issues loading or processing the data

    """
    logger.info("Downloading preprocessed training data from S3...")
    train_data_path = f"s3://{bucket_name}/processed_train.csv"

    try:
        train_df = pd.read_csv(train_data_path)

        if train_df.empty:
            raise DataError("Training data file is empty")

        logger.info(f"Loaded training data with shape: {train_df.shape}")
        return train_df

    except FileNotFoundError:
        error_msg = f"Training data file not found at {train_data_path}"
        logger.error(error_msg)
        raise DataError(error_msg) from None

    except pd.errors.EmptyDataError:
        error_msg = f"Training data file is empty at {train_data_path}"
        logger.error(error_msg)
        raise DataError(error_msg) from None

    except Exception as e:
        error_msg = f"Failed to load training data: {e!s}"
        logger.error(error_msg)
        raise DataError(error_msg) from e


# Load training data
if data_dir:
    train_df = pd.read_csv(Path(data_dir) / "processed_train.csv")
    logger.info(f"Loaded local training data with shape: {train_df.shape}")
else:
    train_df = load_training_data(user_bucket_name)

# Specify the target column
target_column = "Total"


def prepare_features(
    df: pd.DataFrame,
    target_col: str,
    exclude_cols: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare feature matrix and target vector from DataFrame.

    Args:
        df: Input DataFrame
        target_col: Name of target column
        exclude_cols: List of columns to exclude from features

    Returns:
        Tuple containing:
            - Feature matrix (X)
            - Target vector (y)

    """
    logger.info("Preparing features and target...")

    # Split features and target
    xaxis = df.drop(columns=[target_col, *exclude_cols], errors="ignore")
    yaxis = df[target_col]

    # Remove rows with NaN in target variable
    mask = yaxis.notna()
    xaxis = xaxis[mask]
    yaxis = yaxis[mask]

    logger.info(f"Removed {(~mask).sum()} rows with NaN in target variable")

    # Handle categorical features
    categorical_cols = xaxis.select_dtypes(include=["object"]).columns
    logger.info(f"Found {len(categorical_cols)} categorical columns")

    for col in categorical_cols:
        le = LabelEncoder()
        xaxis[col] = le.fit_transform(xaxis[col])

    logger.info(f"Final feature matrix shape: {xaxis.shape}")
    return xaxis, yaxis


# Prepare features
X, y = prepare_features(train_df, target_column, ["ID", "Location"])


def train_model(data_dir: str | None = None) -> RandomForestRegressor:
    """Train a RandomForest regression model.

    Args:
        features: Feature matrix
        target: Target vector
        test_size: Validation split ratio
        random_state: Random seed for reproducibility

    Returns:
        Trained RandomForestRegressor model

    Raises:
        ModelError: If there are issues during model training
        ValueError: If input data is invalid

    """
    if X.empty or y.empty:
        raise ValueError("Input data cannot be empty")

    try:
        logger.info("Splitting data into train/validation sets...")
        features_train, features_val, target_train, target_val = train_test_split(
            features,
            target,
            test_size=test_size,
            random_state=random_state,
        )

        logger.info("Training RandomForestRegressor model...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=random_state,
        )

        model.fit(features_train, target_train)

        # Validate model performance
        val_score = model.score(features_val, target_val)
        logger.info(f"Validation R² score: {val_score:.4f}")

        if val_score < 0:
            logger.warning("Model performance is worse than random prediction")

        return model

    except Exception as e:
        error_msg = f"Error during model training: {e!s}"
        logger.error(error_msg)
        raise ModelError(error_msg) from e


# Train the model
model = train_model(X, y)


def save_model(
    model: RandomForestRegressor,
    bucket_name: str | None = None,
    model_name: str = "random_forest_model.joblib",
    output_dir: str | None = None,
) -> None:
    """Save trained model locally and upload to S3.

    Args:
        model: Trained model to save
        bucket_name: S3 bucket name
        model_name: Name of model file

    """
    # Save locally first
    logger.info("Saving model locally...")
    joblib.dump(model, model_name)

    if output_dir:
        # Save to local output directory
        output_path = Path(output_dir) / model_name
        logger.info(f"Saving model to {output_path}...")
        joblib.dump(model, output_path)
        logger.info("Model saved successfully")
    else:
        # Upload to S3
        model_s3_path = f"s3://{bucket_name}/models/{model_name}"
        logger.info(f"Uploading model to {model_s3_path}...")

        try:
            s3_client.upload_file(model_name, bucket_name, f"models/{model_name}")
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Failed to upload model: {e!s}")
            raise


# Save the trained model
save_model(model, user_bucket_name)
