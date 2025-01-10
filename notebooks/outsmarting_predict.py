# Import necessary libraries
import boto3
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Initialize S3 client and use team bucket
s3_client = boto3.client("s3")
workspace_name = boto3.client("sts").get_caller_identity()["Arn"].split("/")[-1]
# Use the team bucket format - do not create new buckets
bucket_name = f"{workspace_name}-team-bucket"

# Load preprocessed test dataset from S3
print("Downloading preprocessed test dataset from S3...")
test_data_path = f"s3://{bucket_name}/processed_test.csv"
test_df = pd.read_csv(test_data_path)

# Load the trained model from S3
model_s3_path = f"s3://{bucket_name}/models/random_forest_model.joblib"
local_model_path = "random_forest_model.joblib"
print("Downloading trained model from S3...")
s3_client.download_file(bucket_name, "models/random_forest_model.joblib", local_model_path)

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
predictions_s3_path = f"s3://{bucket_name}/predictions/Predictions.csv"
print("Uploading predictions to S3...")
s3_client.upload_file(submission_path, bucket_name, "predictions/Predictions.csv")

print(f"Predictions saved to {predictions_s3_path}")
