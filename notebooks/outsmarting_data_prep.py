# Import necessary libraries
import boto3
import pandas as pd
from scipy.spatial import cKDTree

# Initialize S3 client
s3_client = boto3.client("s3")
bucket_name = "sua-outsmarting-outbreaks-challenge-comp"
out_bucket_name = "comp-user-5ow9bw-team-bucket"


# Helper function to find nearest locations
def find_nearest(hospital_df, location_df, lat_col, lon_col, id_col):
    tree = cKDTree(location_df[[lat_col, lon_col]].values)
    nearest = {}
    for _, row in hospital_df.iterrows():
        _, idx = tree.query([row["Transformed_Latitude"], row["Transformed_Longitude"]])
        nearest[row["ID"]] = location_df.iloc[idx][id_col]
    return nearest


# Load datasets
print("Downloading datasets from S3...")
train = pd.read_csv(f"s3://{bucket_name}/Train.csv")
test = pd.read_csv(f"s3://{bucket_name}/Test.csv")
toilets = pd.read_csv(f"s3://{bucket_name}/toilets.csv")
waste_management = pd.read_csv(f"s3://{bucket_name}/waste_management.csv")
water_sources = pd.read_csv(f"s3://{bucket_name}/water_sources.csv")

# Combine train and test datasets
hospital_data = pd.concat([train, test])


# Preprocess water sources
def preprocess_water_sources(water_sources):
    water_sources.dropna(subset=["water_Transformed_Latitude"], inplace=True)
    water_sources["water_Month_Year_lat_lon"] = (
        water_sources["water_Month_Year"]
        + "_"
        + water_sources["water_Transformed_Latitude"].astype(str)
        + "_"
        + water_sources["water_Transformed_Longitude"].astype(str)
    )
    return water_sources


def preprocess_supplementary_data(df, prefix):
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
print("Uploading processed datasets to S3...")
processed_train = merged_data[merged_data["Year"] < 2023]
processed_test = merged_data[merged_data["Year"] == 2023]

train_output_path = f"s3://{out_bucket_name}/processed_train.csv"
test_output_path = f"s3://{out_bucket_name}/processed_test.csv"

processed_train.to_csv(train_output_path, index=False)
processed_test.to_csv(test_output_path, index=False)

print(f"Processed train dataset saved to {train_output_path}")
print(f"Processed test dataset saved to {test_output_path}")
