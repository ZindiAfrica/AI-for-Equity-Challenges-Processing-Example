"""Visualization utilities for data analysis."""


import matplotlib.pyplot as plt
import pandas as pd


def plot_locations(
    hospital_data: pd.DataFrame,
    water_sources: pd.DataFrame,
    waste_management: pd.DataFrame,
    toilets: pd.DataFrame,
    year: int = 2022,
    month: int = 1,
    month_name: str = "January"
) -> None:
    """Plot facility locations on a map for a specific time period.
    
    Args:
        hospital_data: DataFrame with hospital locations
        water_sources: DataFrame with water source locations
        waste_management: DataFrame with waste management locations
        toilets: DataFrame with toilet locations
        year: Year to plot (2019-2023)
        month: Month number (1-12) 
        month_name: Month name for plot title

    """
    if year < 2019 or year > 2023:
        raise ValueError("Year must be between 2019 and 2023")

    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")

    valid_months = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    if month_name.capitalize() not in valid_months:
        raise ValueError(f"Month name must be one of: {', '.join(valid_months)}")

    plt.figure(figsize=(12, 8))
    subsets = [
        (hospital_data.query(f"Year == {year} and Month == {month}"),
         "Transformed", "Hospital", "s"),
        (water_sources.query(f"water_Month_Year == '{month}_{year}'"),
         "water_Transformed", "Water", "o"),
        (waste_management.query(f"waste_Month_Year == '{month}_{year}'"),
         "waste_Transformed", "Waste", "x"),
        (toilets.query(f"toilet_Month_Year == '{month}_{year}'"),
         "toilet_Transformed", "Toilet", "^"),
    ]

    for df, prefix, label, marker in subsets:
        plt.scatter(df[f"{prefix}_Longitude"],
                   df[f"{prefix}_Latitude"],
                   label=label, alpha=0.6, marker=marker)

    plt.title(f"Locations ({month_name.capitalize()} {year})")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True)
    plt.show()
