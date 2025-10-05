import cartopy.crs as ccrs
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import json
from matplotlib import rcParams
import sqlite3

rcParams["figure.dpi"] = 80  # Reduce figure resolution to keep file size low

# Authenticate
auth = earthaccess.login()

if not auth.authenticated:
    auth.login(strategy="interactive", persist=True)

print("earthaccess version:", earthaccess.__version__)

# Search for TEMPO NO₂ Level-3 product
results = earthaccess.search_data(
    short_name="TEMPO_NO2_L3",
    version="V03",
    temporal=("2025-09-1 12:00", "2025-09-14 12:00"),
    count=14,
)

print(f"Number of granules found: {len(results)}")

# Open virtual multi-file dataset
open_options = {
    "access": "indirect",  # access to cloud data (faster in AWS with "direct")
    "load": True,
    "concat_dim": "time",
    "data_vars": "minimal",
    "coords": "minimal",
    "compat": "override",
    "combine_attrs": "override",
}

result_root = earthaccess.open_virtual_mfdataset(granules=results, **open_options)
result_product = earthaccess.open_virtual_mfdataset(granules=results, group="product", **open_options)
result_geolocation = earthaccess.open_virtual_mfdataset(granules=results, group="geolocation", **open_options)

# Merge the datasets
result_merged = xr.merge([result_root, result_product, result_geolocation])

# Define region of interest
lon_bounds = (-137, -50)
lat_bounds = (17, 56)

print(
    f"Analyzing region: {lat_bounds[0]}°N to {lat_bounds[1]}°N, "
    f"{abs(lon_bounds[0])}°W to {abs(lon_bounds[1])}°W"
)

# Subset to region and compute temporal mean
temporal_mean_ds = (
    result_merged.sel(
        longitude=slice(lon_bounds[0], lon_bounds[1]),
        latitude=slice(lat_bounds[0], lat_bounds[1]),
    )
    .where(result_merged["main_data_quality_flag"] == 0)
    .mean(dim="time")
)

print(f"Dataset shape after subsetting: {temporal_mean_ds.dims}")

# Compute the mean vertical column
mean_vertical_column_trop = temporal_mean_ds["vertical_column_troposphere"].compute()

# --- Convert to list of [lat, lon, mean_trop] ---
lats = mean_vertical_column_trop["latitude"].values
lons = mean_vertical_column_trop["longitude"].values
data = mean_vertical_column_trop.values

# Ensure arrays align and flatten
lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
triplets = np.column_stack((lat_grid.flatten(), lon_grid.flatten(), data.flatten()))

# Filter out NaN values
triplets = triplets[~np.isnan(triplets[:, 2])]

# Convert to list of lists
triplet_list = triplets.tolist()

print(f"Extracted {len(triplet_list)} data points")

# Define your magnitude threshold
magnitude = 0.2 * (10 ** 16)  # 2e15

# Filter triplets: keep only points with value <= magnitude
# filtered_triplets = [t for t in triplet_list if t[2] >= magnitude]
filtered_triplets = []

max_value = 0

for t in triplet_list:
    if t[2] >= magnitude:
        filtered_triplets.append(t)
    
    # # Set negative data to be 0
    # if t[2] < 0:
    #     t[2] = 0

    if t[2] > max_value:
        max_value = t[2]

for list in filtered_triplets:
    list[2] = 0.5 + (list[2] / max_value * 0.5)

print(f"Kept {len(filtered_triplets)} of {len(triplet_list)} data points")

# Save filtered data to SQLite
conn = sqlite3.connect("tempo_no2.db")
cursor = conn.cursor()

# Create a table for NO₂ data (if it doesn't exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS no2_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL,
    longitude REAL,
    value REAL
)
""")

# Clear existing data (optional - remove if you want to append)
cursor.execute("DELETE FROM no2_data")

# Insert the triplets
cursor.executemany(
    "INSERT INTO no2_data (latitude, longitude, value) VALUES (?, ?, ?)",
    filtered_triplets
)

# Commit the transaction
conn.commit()

# Verify the data was saved
cursor.execute("SELECT COUNT(*) FROM no2_data")
count = cursor.fetchone()[0]
print(f"Total rows in database: {count}")

# Fetch the first few rows
cursor.execute("SELECT latitude, longitude, value FROM no2_data LIMIT 5")
rows = cursor.fetchall()

print("\nFirst 5 entries:")
for r in rows:
    print(f"Lat: {r[0]:.4f}, Lon: {r[1]:.4f}, Value: {r[2]:.4e}")

# Close the connection
conn.close()
