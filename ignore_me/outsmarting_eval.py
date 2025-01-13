# Import necessary libraries
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib
import boto3

# Initialize S3 client
s3_client = boto3.client('s3')
bucket_name = 'comp-user-5ow9bw-team-bucket'

# Load preprocessed datasets from S3
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

# Specify the target column
target_column = 'Total'

# Prepare the test data
X_test = test_df.drop(columns=[target_column, 'ID', 'Location'], errors='ignore')  # Exclude unnecessary columns
y_test = test_df[target_column]

# Remove any rows with NaN values
mask = y_test.notna()
X_test = X_test[mask]
y_test = y_test[mask]

logger.info(f"Removed {(~mask).sum()} rows with NaN in target variable")

# Handle categorical features in the test data
categorical_cols = X_test.select_dtypes(include=['object']).columns
for col in categorical_cols:
    le = LabelEncoder()
    X_test[col] = le.fit_transform(X_test[col])

# Align test dataset with training features
for col in model.feature_names_in_:
    if col not in X_test.columns:
        X_test[col] = 0  # Add missing feature with default value (e.g., zero)

X_test = X_test[model.feature_names_in_]

# Evaluate the model
print("Evaluating the model...")
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

# Save evaluation metrics
evaluation_metrics = {
    "mean_absolute_error": mae
}
print(f"Mean Absolute Error (MAE): {mae}")

# Upload evaluation metrics to S3
metrics_path = "evaluation_metrics.json"
with open(metrics_path, "w") as f:
    f.write(str(evaluation_metrics))

metrics_s3_path = f"s3://{bucket_name}/evaluation/evaluation_metrics.json"
print("Uploading evaluation metrics to S3...")
s3_client.upload_file(metrics_path, bucket_name, "evaluation/evaluation_metrics.json")

print(f"Evaluation metrics saved to {metrics_s3_path}")

