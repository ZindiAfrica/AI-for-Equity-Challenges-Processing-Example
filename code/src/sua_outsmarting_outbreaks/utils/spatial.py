"""Spatial analysis utilities."""


import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def find_nearest_locations(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    id_col: str,
    max_distance: float = None
) -> dict[str, str]:
    """Find nearest locations using KD-tree spatial indexing.
    
    Args:
        source_df: DataFrame containing source points
        target_df: DataFrame containing target points to find nearest from
        lat_col: Name of latitude column
        lon_col: Name of longitude column 
        id_col: Name of ID column to return
        max_distance: Optional maximum distance threshold
        
    Returns:
        Dictionary mapping source IDs to nearest target IDs

    """
    # Create KD-tree for efficient nearest neighbor search
    tree = cKDTree(target_df[[lat_col, lon_col]].values)

    # Find nearest neighbors
    nearest = {}
    for _, row in source_df.iterrows():
        dist, idx = tree.query([row["Transformed_Latitude"],
                              row["Transformed_Longitude"]])

        # Only include if within distance threshold
        if max_distance is None or dist <= max_distance:
            nearest[row["ID"]] = target_df.iloc[idx][id_col]

    return nearest

def calculate_distances(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    lat_col: str = "Transformed_Latitude",
    lon_col: str = "Transformed_Longitude"
) -> np.ndarray:
    """Calculate distances between all source and target points.
    
    Args:
        source_df: DataFrame with source points
        target_df: DataFrame with target points
        lat_col: Name of latitude column
        lon_col: Name of longitude column
        
    Returns:
        Array of distances between each source-target pair

    """
    source_coords = source_df[[lat_col, lon_col]].values
    target_coords = target_df[[lat_col, lon_col]].values

    tree = cKDTree(target_coords)
    distances, _ = tree.query(source_coords)

    return distances
