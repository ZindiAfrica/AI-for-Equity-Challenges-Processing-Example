import logging
import sys

import boto3
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_execution_role,
    get_user_bucket_name,
    get_user_name,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Initialize AWS Resources
# ----------------------------------------
logger.info("\nInitializing AWS resources...")
s3_client = boto3.client("s3")


username = get_user_name()
role = get_execution_role()
data_bucket_name = get_data_bucket_name()
user_bucket_name = get_user_bucket_name()

# Define common tags
tags = [{"Key": "team", "Value": username}]

logger.info(f"Using S3 bucket: {user_bucket_name}")

# Define common tags
tags = [{"Key": "team", "Value": username}]

# ----------------------------------------
# Load Test Dataset
# ----------------------------------------
logger.info("\nStarting model evaluation process...")
logger.info("Downloading preprocessed test dataset from S3...")
test_data_path = f"s3://{user_bucket_name}/processed_test.csv"
logger.info(f"Reading test data from: {test_data_path}")
test_df = pd.read_csv(test_data_path)
logger.info(f"Test dataset shape: {test_df.shape}")

# Load the trained model from S3
model_s3_path = f"s3://{user_bucket_name}/models/random_forest_model.joblib"
local_model_path = "random_forest_model.joblib"
logger.info("Downloading trained model from S3...")
s3_client.download_file(user_bucket_name, "models/random_forest_model.joblib", local_model_path)
logger.info("Loading model into memory...")
model = joblib.load(local_model_path)
logger.info("Model loaded successfully")

# Specify the target column
target_column = "Total"

# Prepare the test data
logger.info("Preparing test data for evaluation...")
X_test = test_df.drop(columns=[target_column, "ID", "Location"], errors="ignore")
y_test = test_df[target_column]
logger.info(f"Features shape: {X_test.shape}, Target shape: {y_test.shape}")

# ----------------------------------------
# Process Categorical Features
# ----------------------------------------
logger.info("\nProcessing categorical features...")
categorical_cols = X_test.select_dtypes(include=["object"]).columns
logger.info(f"Found {len(categorical_cols)} categorical columns: {list(categorical_cols)}")

for col in categorical_cols:
    logger.debug(f"Encoding column: {col}")
    le = LabelEncoder()
    X_test[col] = le.fit_transform(X_test[col])

# ----------------------------------------
# Align Features
# ----------------------------------------
logger.info("\nAligning features with training data...")
missing_cols = set(model.feature_names_in_) - set(X_test.columns)
if missing_cols:
    logger.warning(f"Adding missing columns with zero values: {missing_cols}")
    for col in model.feature_names_in_:
        if col not in X_test.columns:
            X_test[col] = 0

X_test = X_test[model.feature_names_in_]
logger.info(f"Final feature matrix shape: {X_test.shape}")

# ----------------------------------------
# Model Evaluation
# ----------------------------------------
logger.info("\nMaking predictions on test data...")
y_pred = model.predict(X_test)
logger.info("Calculating evaluation metrics...")
mae = mean_absolute_error(y_test, y_pred)

# ----------------------------------------
# Save and Upload Results
# ----------------------------------------
logger.info("\nSaving evaluation results...")
evaluation_metrics = {"mean_absolute_error": mae}
logger.info(f"Model Performance - Mean Absolute Error (MAE): {mae:.4f}")

# Save metrics locally
logger.info("Writing metrics to file...")
metrics_path = "evaluation_metrics.json"
with open(metrics_path, "w") as f:
    f.write(str(evaluation_metrics))

# Upload to S3
metrics_s3_path = f"s3://{user_bucket_name}/evaluation/evaluation_metrics.json"
logger.info(f"Uploading metrics to {metrics_s3_path}")
s3_client.upload_file(metrics_path, user_bucket_name, "evaluation/evaluation_metrics.json")

logger.info("\nEvaluation process completed successfully")
