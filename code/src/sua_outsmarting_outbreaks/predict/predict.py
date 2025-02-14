"""Prediction module for generating model predictions on test data."""


import boto3
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from sua_outsmarting_outbreaks.utils.aws_utils import (
    initialize_aws_resources,
)
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)


def generate_predictions(data_dir: str | None = None) -> None:
    """Generate predictions on test data using trained model.

    Args:
    ----
        data_dir: Optional local directory containing test data and model

    """
    # Initialize AWS resources
    s3_client = boto3.client("s3")
    username, role, data_bucket_name, user_bucket_name, tags = initialize_aws_resources()

    # Load preprocessed test dataset from S3
    logger.info("Downloading preprocessed test dataset from S3...")
    test_data_path = f"s3://{user_bucket_name}/processed_test.csv"
    test_df = pd.read_csv(test_data_path)

    # Load the trained model from S3
    model_s3_path = f"s3://{user_bucket_name}/models/random_forest_model.joblib"
    local_model_path = "random_forest_model.joblib"
    logger.info("Downloading trained model from S3...")
    s3_client.download_file(user_bucket_name, "models/random_forest_model.joblib", local_model_path)

    # Load the model
    model = joblib.load(local_model_path)

    # Prepare the test data
    X_test = test_df.drop(columns=["Total", "ID", "Location"], errors="ignore")

    # Handle categorical features in the test data
    categorical_cols = X_test.select_dtypes(include=["object"]).columns
    for col in categorical_cols:
        le = LabelEncoder()
        X_test[col] = le.fit_transform(X_test[col])

    # Align test dataset with training features
    for col in model.feature_names_in_:
        if col not in X_test.columns:
            X_test[col] = 0  # Add missing feature with default value

    X_test = X_test[model.feature_names_in_]

    # Make predictions
    logger.info("Making predictions on test data...")
    predictions = model.predict(X_test)

    # Create the final DataFrame with ID and predictions
    submission = test_df[["ID"]].copy()
    submission["Predicted_Total"] = predictions

    # Save predictions to a CSV file
    submission_path = "Predictions.csv"
    submission.to_csv(submission_path, index=False)

    # Upload predictions to S3
    predictions_s3_path = f"s3://{user_bucket_name}/predictions/Predictions.csv"
    logger.info("Uploading predictions to S3...")
    s3_client.upload_file(submission_path, user_bucket_name, "predictions/Predictions.csv")

    logger.info(f"Predictions saved to {predictions_s3_path}")
