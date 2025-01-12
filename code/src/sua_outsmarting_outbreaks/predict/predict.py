# Import necessary libraries
import boto3
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_execution_role,
    get_script_processor_type,
    get_user_bucket_name,
    get_user_name,
)

# Initialize S3 client and use team bucket
s3_client = boto3.client("s3")

username = get_user_name()
role = get_execution_role()
data_bucket_name = get_data_bucket_name()
user_bucket_name = get_user_bucket_name()

# Define common tags
tags = [{"Key": "team", "Value": username}]

# Define common tags
tags = [{"Key": "team", "Value": username}]

# Load preprocessed test dataset from S3
print("Downloading preprocessed test dataset from S3...")
test_data_path = f"s3://{user_bucket_name}/processed_test.csv"
test_df = pd.read_csv(test_data_path)

# Load the trained model from S3
model_s3_path = f"s3://{user_bucket_name}/models/random_forest_model.joblib"
local_model_path = "random_forest_model.joblib"
print("Downloading trained model from S3...")
s3_client.download_file(user_bucket_name, "models/random_forest_model.joblib", local_model_path)

# Load the model
model = joblib.load(local_model_path)

# Prepare the test data
X_test = test_df.drop(columns=["Total", "ID", "Location"], errors="ignore")  # Exclude unnecessary columns

# Handle categorical features in the test data
categorical_cols = X_test.select_dtypes(include=["object"]).columns
for col in categorical_cols:
    le = LabelEncoder()
    X_test[col] = le.fit_transform(X_test[col])

# Align test dataset with training features
for col in model.feature_names_in_:
    if col not in X_test.columns:
        X_test[col] = 0  # Add missing feature with default value (e.g., zero)

X_test = X_test[model.feature_names_in_]

# Make predictions
print("Making predictions on test data...")
predictions = model.predict(X_test)

# Create the final DataFrame with ID and predictions
submission = test_df[["ID"]].copy()
submission["Predicted_Total"] = predictions

# Save predictions to a CSV file
submission_path = "Predictions.csv"
submission.to_csv(submission_path, index=False)

# Upload predictions to S3
predictions_s3_path = f"s3://{user_bucket_name}/predictions/Predictions.csv"
print("Uploading predictions to S3...")
s3_client.upload_file(submission_path, user_bucket_name, "predictions/Predictions.csv")

print(f"Predictions saved to {predictions_s3_path}")
