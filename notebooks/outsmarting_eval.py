import logging
import sys
import boto3
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize S3 client and use team bucket
logger.info("Initializing AWS S3 client...")
s3_client = boto3.client("s3")
workspace_name = boto3.client("sts").get_caller_identity()["Arn"].split("/")[-1]
bucket_name = f"{workspace_name}-team-bucket"
logger.info(f"Using S3 bucket: {bucket_name}")

# Load preprocessed datasets from S3
logger.info("Starting model evaluation process...")
logger.info("Downloading preprocessed test dataset from S3...")
test_data_path = f"s3://{bucket_name}/processed_test.csv"
test_df = pd.read_csv(test_data_path)

# Load the trained model from S3
model_s3_path = f"s3://{bucket_name}/models/random_forest_model.joblib"
local_model_path = "random_forest_model.joblib"
print("Downloading trained model from S3...")
s3_client.download_file(bucket_name, "models/random_forest_model.joblib", local_model_path)

# Load the model
model = joblib.load(local_model_path)

# Specify the target column
target_column = "Total"

# Prepare the test data
logger.info("Preparing test data for evaluation...")
X_test = test_df.drop(columns=[target_column, "ID", "Location"], errors="ignore")
y_test = test_df[target_column]
logger.info(f"Features shape: {X_test.shape}, Target shape: {y_test.shape}")

# Handle categorical features in the test data
logger.info("Processing categorical features...")
categorical_cols = X_test.select_dtypes(include=["object"]).columns
logger.info(f"Found {len(categorical_cols)} categorical columns: {list(categorical_cols)}")
for col in categorical_cols:
    logger.debug(f"Encoding column: {col}")
    le = LabelEncoder()
    X_test[col] = le.fit_transform(X_test[col])

# Align test dataset with training features
logger.info("Aligning features with training data...")
missing_cols = set(model.feature_names_in_) - set(X_test.columns)
if missing_cols:
    logger.warning(f"Adding missing columns with zero values: {missing_cols}")
    for col in model.feature_names_in_:
        if col not in X_test.columns:
            X_test[col] = 0

X_test = X_test[model.feature_names_in_]
logger.info(f"Final feature matrix shape: {X_test.shape}")

# Evaluate the model
logger.info("Making predictions on test data...")
y_pred = model.predict(X_test)
logger.info("Calculating evaluation metrics...")
mae = mean_absolute_error(y_test, y_pred)

# Save evaluation metrics
evaluation_metrics = {"mean_absolute_error": mae}
logger.info(f"Model Performance - Mean Absolute Error (MAE): {mae:.4f}")

# Upload evaluation metrics to S3
logger.info("Saving evaluation metrics...")
metrics_path = "evaluation_metrics.json"
with open(metrics_path, "w") as f:
    f.write(str(evaluation_metrics))

metrics_s3_path = f"s3://{bucket_name}/evaluation/evaluation_metrics.json"
logger.info(f"Uploading metrics to {metrics_s3_path}")
s3_client.upload_file(metrics_path, bucket_name, "evaluation/evaluation_metrics.json")

logger.info("Evaluation process completed successfully")
