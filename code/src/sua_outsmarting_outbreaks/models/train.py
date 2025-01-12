"""Model training module for the SUA Outsmarting Outbreaks Challenge.

This module handles the training of a RandomForest regression model using preprocessed data.
It includes data loading, feature engineering, model training and model artifact storage.

Example:
    This script is typically run as part of the SageMaker processing job:
    >>> python -m sua_outsmarting_outbreaks.models.train
"""

import logging
import sys
from typing import Tuple

import boto3
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
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

print(f"\nUsing team bucket: {user_bucket_name}")
print("Using instance: ml.g4dn.8xlarge")
print("- NVIDIA T4 GPU with 16GB memory")
print("- 32 vCPUs and 128GB RAM")
print("- Network: 50 Gigabit")
print("- EBS: 9500 MBps bandwidth, 40K IOPS")
print("- Cost: $2.72/hr (on-demand) or $0.816/hr (spot)")


def load_training_data(bucket_name: str) -> pd.DataFrame:
    """Load preprocessed training data from S3.

    Args:
        bucket_name: Name of the S3 bucket containing the data

    Returns:
        DataFrame containing the training data

    Raises:
        FileNotFoundError: If the training data file doesn't exist
        pd.errors.EmptyDataError: If the training data file is empty

    """
    logger.info("Downloading preprocessed training data from S3...")
    train_data_path = f"s3://{bucket_name}/processed_train.csv"
    try:
        train_df = pd.read_csv(train_data_path)
        logger.info(f"Loaded training data with shape: {train_df.shape}")
        return train_df
    except Exception as e:
        logger.error(f"Failed to load training data: {e!s}")
        raise


# Load training data
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
    X = df.drop(columns=[target_col] + exclude_cols, errors="ignore")
    y = df[target_col]

    # Handle categorical features
    categorical_cols = X.select_dtypes(include=["object"]).columns
    logger.info(f"Found {len(categorical_cols)} categorical columns")

    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])

    logger.info(f"Final feature matrix shape: {X.shape}")
    return X, y


# Prepare features
X, y = prepare_features(train_df, target_column, ["ID", "Location"])


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> RandomForestRegressor:
    """Train a RandomForest regression model.

    Args:
        X: Feature matrix
        y: Target vector
        test_size: Validation split ratio
        random_state: Random seed for reproducibility

    Returns:
        Trained RandomForestRegressor model

    """
    logger.info("Splitting data into train/validation sets...")
    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
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
    model.fit(X_train, y_train)

    # Log validation score
    val_score = model.score(X_val, y_val)
    logger.info(f"Validation R² score: {val_score:.4f}")

    return model


# Train the model
model = train_model(X, y)


def save_model(
    model: RandomForestRegressor,
    bucket_name: str,
    model_name: str = "random_forest_model.joblib",
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
