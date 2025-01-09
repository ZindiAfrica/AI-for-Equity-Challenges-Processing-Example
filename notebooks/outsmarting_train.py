# Import necessary libraries
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import boto3

# Initialize S3 client
s3_client = boto3.client("s3")
bucket_name = "comp-user-5ow9bw-team-bucket"


# Load preprocessed datasets from S3
print("Downloading preprocessed datasets from S3...")
train_data_path = f"s3://{bucket_name}/processed_train.csv"
train_df = pd.read_csv(train_data_path)

# Specify the target column
target_column = "Total"

# Feature and target split
X = train_df.drop(
    columns=[target_column, "ID", "Location"], errors="ignore"
)  # Exclude unnecessary columns
y = train_df[target_column]

# Handle categorical features
categorical_cols = X.select_dtypes(include=["object"]).columns
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])

# Split the dataset
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the regression model
print("Training the RandomForestRegressor model...")
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Save the trained model to a local file
model_path = "random_forest_model.joblib"
joblib.dump(model, model_path)

# Upload the trained model to S3
model_s3_path = f"s3://{bucket_name}/models/random_forest_model.joblib"
print("Uploading the trained model to S3...")
s3_client.upload_file(model_path, bucket_name, "models/random_forest_model.joblib")

print(f"Trained model saved to {model_s3_path}")
