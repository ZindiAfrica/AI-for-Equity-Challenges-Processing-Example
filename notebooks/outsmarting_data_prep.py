# Import necessary libraries
import pandas as pd
import boto3
from scipy.spatial import cKDTree

# Initialize S3 client
s3_client = boto3.client('s3')
bucket_name = 'sua-outsmarting-outbreaks-challenge-comp'
out_bucket_name = 'comp-user-5ow9bw-team-bucket/data_prep'

# Helper function to find nearest locations
def find_nearest(hospital_df, location_df, lat_col, lon_col, id_col):
    location_df = location_df[np.isfinite(location_df[[lat_col, lon_col]]).all(axis=1)]
    tree = cKDTree(location_df[[lat_col, lon_col]].values)
    nearest = {}
    for _, row in hospital_df.iterrows():
        _, idx = tree.query([row['Transformed_Latitude'], row['Transformed_Longitude']])
        nearest[row['ID']] = location_df.iloc[idx][id_col]
    return nearest

# Rename columns for clarity
def rename_columns(df, prefix):
    for col in df.columns:
        if col not in ['Month_Year_lat_lon', 'lat_lon']:
            df.rename(columns={col: f"{prefix}_{col}"}, inplace=True)

# Preprocess water sources
def preprocess_water_sources(water_sources):
    water_sources.dropna(subset=['water_Transformed_Latitude'], inplace=True)
    water_sources['water_Month_Year_lat_lon'] = (
        water_sources['water_Month_Year'] + '_' +
        water_sources['water_Transformed_Latitude'].astype(str) + '_' +
        water_sources['water_Transformed_Longitude'].astype(str)
    )
    return water_sources

def preprocess_supplementary_data(df, prefix):
    df[f"{prefix}_Month_Year_lat_lon"] = (
        df[f"{prefix}_Month_Year"] + '_' +
        df[f"{prefix}_Transformed_Latitude"].astype(str) + '_' +
        df[f"{prefix}_Transformed_Longitude"].astype(str)
    )
    return df


# Load datasets

print("Downloading datasets from S3...")
data_path = f"s3://{bucket_name}"
train = pd.read_csv(f"{data_path}/Train.csv")
test = pd.read_csv(f"{data_path}/Test.csv")
toilets = pd.read_csv(f"{data_path}/toilets.csv")
waste_management = pd.read_csv(f"{data_path}/waste_management.csv")
water_sources = pd.read_csv(f"{data_path}/water_sources.csv")


# Combine train and test datasets
hospital_data = pd.concat([train, test])

# Drop unnecessary columns from supplementary datasets
for df in [toilets, waste_management, water_sources]:
    df.drop(columns=['Year', 'Month'], inplace=True)

rename_columns(toilets, "toilet")
rename_columns(waste_management, "waste")
rename_columns(water_sources, "water")

# Fill missing values in the 'Total' column
# Replace NaN values in 'Total' column with 0 without using inplace=True
hospital_data['Total'] = hospital_data['Total'].fillna(0)

water_sources = preprocess_water_sources(water_sources)
toilets = preprocess_supplementary_data(toilets, 'toilet')
waste_management = preprocess_supplementary_data(waste_management, 'waste')

# Merge datasets with nearest locations
merged_data = hospital_data.copy()
datasets = [
    (toilets, 'toilet', 'toilet_Month_Year_lat_lon'),
    (waste_management, 'waste', 'waste_Month_Year_lat_lon'),
    (water_sources, 'water', 'water_Month_Year_lat_lon'),
]

for df, prefix, id_col in datasets:
    nearest = find_nearest(merged_data, df, f"{prefix}_Transformed_Latitude",
                           f"{prefix}_Transformed_Longitude", id_col)
    nearest_df = pd.DataFrame(list(nearest.items()), columns=['ID', id_col])
    merged_data = merged_data.merge(nearest_df, on="ID").merge(df, on=id_col)

# Save processed datasets to S3
print("Uploading processed datasets to S3...")
processed_train = merged_data[merged_data['Year'] < 2023]
processed_test = merged_data[merged_data['Year'] == 2023]

train_output_path = f"s3://{out_bucket_name}/processed_train.csv"
test_output_path = f"s3://{out_bucket_name}/processed_test.csv"

processed_train.to_csv(train_output_path, index=False)
processed_test.to_csv(test_output_path, index=False)

print(f"Processed train dataset saved to {train_output_path}")
print(f"Processed test dataset saved to {test_output_path}")
