import os
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Try to import cartopy, but don't fail if not available
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False
    print("Note: cartopy not installed. Using basic plotting. Install with: conda install -c conda-forge cartopy")


def open_local_datasets(folder_path, engine="netcdf4", time_dim="Line", start_date="2000-01-01", file_pattern="*.he5.nc"):
    """
    Open and concatenate NetCDF/HDF-EOS5 files from a folder.
    
    Parameters:
    -----------
    folder_path : str
        Path to folder containing NetCDF files
    engine : str
        Engine to use: 'netcdf4' for .he5.nc files (recommended), 'h5netcdf' also works
    time_dim : str
        Dimension name to concatenate along
    start_date : str
        Start date for time coordinate (format: 'YYYY-MM-DD')
    file_pattern : str
        File pattern to match (e.g., "*.he5.nc", "*.nc")
    
    Returns:
    --------
    xarray.Dataset
    """
    # Get file extension from pattern
    file_extension = file_pattern.replace("*", "")
    
    # Get all matching files
    files = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.endswith(file_extension)
    ]
    
    if not files:
        raise FileNotFoundError(f"No {file_extension} files found in {folder_path}")
    
    # Open datasets lazily and concatenate
    ds = xr.open_mfdataset(
        files,
        combine="nested",
        concat_dim=time_dim,
        parallel=False,
        engine=engine
    )
    
    # Create time coordinate if dimension exists but coordinate doesn't
    if time_dim in ds.dims and time_dim not in ds.coords:
        ds = ds.assign_coords({
            time_dim: pd.date_range(start_date, periods=ds.dims[time_dim])
        })
    
    return ds


def check_variable(ds, variable_name):
    """Check if variable exists in dataset and print info."""
    if variable_name in ds.data_vars:
        print(f"✓ {variable_name} found in dataset")
        print(ds[variable_name])
        return True
    else:
        print(f"✗ {variable_name} not found in dataset")
        print(f"Available variables: {list(ds.data_vars)}")
        return False


def plot_global_mean(ds, variable_name, time_dim="Line"):
    """
    Plot global mean time series of a variable.
    
    Parameters:
    -----------
    ds : xarray.Dataset
        Dataset containing the variable
    variable_name : str
        Name of variable to plot
    time_dim : str
        Name of time dimension
    """
    if variable_name not in ds.data_vars:
        print(f"Cannot plot: {variable_name} not found")
        return
    
    var = ds[variable_name]
    
    # Load data if it's a dask array
    if hasattr(var.data, 'compute'):
        print("Loading dask array into memory...")
        var = var.compute()
    
    # Get all dimension names except time
    dims_to_average = [d for d in var.dims if d != time_dim]
    
    print(f"Variable dimensions: {var.dims}")
    print(f"Averaging over: {dims_to_average}")
    
    # Calculate mean across all non-time dimensions, ignoring NaN values
    if dims_to_average:
        mean_series = var.mean(dim=dims_to_average, skipna=True)
    else:
        mean_series = var  # Already 1D
    
    print(f"Result shape: {mean_series.shape}")
    print(f"Result values: {mean_series.values}")
    
    # Create plot
    plt.figure(figsize=(12, 6))
    
    # Check if we have valid (non-NaN) data
    if mean_series.size > 0:
        # Get the actual values
        values = mean_series.values
        
        # Handle scalar (0-d) or array
        if mean_series.ndim == 0:
            # Single value - plot as bar or point
            if not pd.isna(values):
                plt.bar([0], [float(values)], color='steelblue', alpha=0.7)
                plt.xticks([0], ['Global Mean'])
                plt.ylabel(variable_name)
                plt.title(f"Global Mean {variable_name}")
                plt.grid(True, alpha=0.3, axis='y')
                plt.tight_layout()
                plt.show()
            else:
                print(f"⚠️  Result is NaN - all spatial values were NaN")
        else:
            # Time series - use regular plot
            times = mean_series[time_dim].values
            if not all(pd.isna(values)):
                plt.plot(times, values, marker='o', linestyle='-', markersize=8)
                plt.title(f"Global Mean {variable_name}")
                plt.xlabel("Time")
                plt.ylabel(variable_name)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.show()
            else:
                print(f"⚠️  No valid data to plot - all values are NaN")
    else:
        print(f"⚠️  No data to plot")


def plot_spatial_map(ds, variable_name, time_index=0, cmap='viridis', figsize=(16, 10), interactive=True):
    """
    Plot spatial map of a variable on a world map (interactive with Plotly by default).
    
    Parameters:
    -----------
    ds : xarray.Dataset
        Dataset containing the variable
    variable_name : str
        Name of variable to plot
    time_index : int
        Which time step to plot (default: 0 for first)
    cmap : str
        Colormap to use
    figsize : tuple
        Figure size (width, height) - only for matplotlib
    interactive : bool
        If True, create interactive Plotly map. If False, use matplotlib.
    """
    if variable_name not in ds.data_vars:
        print(f"Cannot plot: {variable_name} not found")
        return
    
    var = ds[variable_name]
    
    # Load data if it's a dask array
    if hasattr(var.data, 'compute'):
        print("Loading dask array into memory...")
        var = var.compute()
    
    # Select the time slice if there's a time dimension
    if 'Line' in var.dims:
        if var.sizes['Line'] > 1:
            data_slice = var.isel(Line=time_index)
            time_label = f" at time index {time_index}"
        else:
            data_slice = var.squeeze('Line')
            time_label = ""
    else:
        data_slice = var
        time_label = ""
    
    # Get lat/lon
    lons = data_slice['lon'].values
    lats = data_slice['lat'].values
    values = data_slice.values
    
    # Print statistics
    valid_data = values[~pd.isna(values)]
    if len(valid_data) > 0:
        print(f"\nStatistics:")
        print(f"  Min: {valid_data.min():.2e}")
        print(f"  Max: {valid_data.max():.2e}")
        print(f"  Mean: {valid_data.mean():.2e}")
        print(f"  Valid pixels: {len(valid_data)} / {values.size} ({100*len(valid_data)/values.size:.1f}%)")
    else:
        print("\n⚠️  No valid data in this slice")
        return
    
    if interactive:
        # Create interactive Plotly map
        fig = go.Figure()
        
        # Add heatmap
        fig.add_trace(go.Heatmap(
            z=values,
            x=lons,
            y=lats,
            colorscale=cmap,
            colorbar=dict(
                title=dict(
                    text=f"{variable_name} ({var.attrs.get('units', '')})",
                    side='right'
                )
            ),
            hovertemplate='Lon: %{x:.2f}<br>Lat: %{y:.2f}<br>Value: %{z:.2e}<extra></extra>'
        ))
        
        # Update layout with map background
        fig.update_layout(
            title=dict(
                text=f'{variable_name}{time_label}',
                x=0.5,
                xanchor='center',
                font=dict(size=18)
            ),
            xaxis=dict(
                title='Longitude',
                showgrid=True,
                gridcolor='lightgray',
                zeroline=False
            ),
            yaxis=dict(
                title='Latitude',
                showgrid=True,
                gridcolor='lightgray',
                zeroline=False,
                scaleanchor='x',
                scaleratio=1
            ),
            width=1200,
            height=700,
            hovermode='closest',
            plot_bgcolor='white'
        )
        
        fig.show()
        
    else:
        # Matplotlib version (static)
        if HAS_CARTOPY:
            # Create figure with map projection
            fig = plt.figure(figsize=figsize)
            ax = plt.axes(projection=ccrs.PlateCarree())
            
            # Add map features
            ax.coastlines(linewidth=0.5)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
            ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
            ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
            
            # Plot data
            im = ax.pcolormesh(
                lons, lats, values,
                transform=ccrs.PlateCarree(),
                cmap=cmap,
                shading='auto'
            )
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05, shrink=0.7)
            cbar.set_label(f'{variable_name} ({var.attrs.get("units", "")})', fontsize=12)
            
            # Set map extent to data bounds
            ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=ccrs.PlateCarree())
            
            # Add gridlines
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            
            ax.set_title(f'{variable_name}{time_label}', fontsize=14, fontweight='bold')
        else:
            # Fallback to basic matplotlib plotting
            fig, ax = plt.subplots(figsize=figsize)
            
            # Plot data
            im = ax.pcolormesh(lons, lats, values, cmap=cmap, shading='auto')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05, shrink=0.7)
            cbar.set_label(f'{variable_name} ({var.attrs.get("units", "")})', fontsize=12)
            
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.set_title(f'{variable_name}{time_label}', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_aspect('equal', adjustable='box')
        
        plt.tight_layout()
        plt.show()


def get_spatial_data_as_list(ds, variable_name, time_index=0, skip_nan=True):
    """
    Extract spatial data as list of [latitude, longitude, value].
    
    Parameters:
    -----------
    ds : xarray.Dataset
        Dataset containing the variable
    variable_name : str
        Name of variable to extract
    time_index : int
        Which time step to extract (default: 0 for first)
    skip_nan : bool
        Whether to skip NaN values (default: True)
    
    Returns:
    --------
    list of lists
        Each inner list is [lat, lon, value]
    """
    if variable_name not in ds.data_vars:
        print(f"Cannot extract: {variable_name} not found")
        return []
    
    var = ds[variable_name]
    
    # Load data if it's a dask array
    if hasattr(var.data, 'compute'):
        print("Loading dask array into memory...")
        var = var.compute()
    
    # Select the time slice if there's a time dimension
    if 'Line' in var.dims:
        if var.sizes['Line'] > 1:
            data_slice = var.isel(Line=time_index)
        else:
            data_slice = var.squeeze('Line')
    else:
        data_slice = var
    
    # Get lat/lon coordinates
    lats = data_slice['lat'].values
    lons = data_slice['lon'].values
    values = data_slice.values
    
    # Build list of [lat, lon, value]
    result = []
    for i in range(lats.shape[0]):
        for j in range(lons.shape[0]):
            val = values[i, j]
            if not skip_nan or not pd.isna(val):
                result.append([float(lats[i]), float(lons[j]), float(val)])
    
    print(f"Extracted {len(result)} data points")
    return result


# ============================================
# Main execution
# ============================================

# Set folder path
folder = "./nasa_data/"

# Open dataset (use netcdf4 for .he5.nc files)
ds = open_local_datasets(folder, engine="netcdf4", file_pattern="*.he5.nc")
print(ds)

# Check and analyze specific variable
variable_name = "ColumnAmountNO2"

if check_variable(ds, variable_name):
    # Print dataset info
    print("\nDataset Size:", ds.nbytes / 1e9, "GB")
    print("Dimensions:", dict(ds.dims))
    
    # Show data array info for the variable
    print(f"\n{variable_name} array:")
    print(ds[variable_name].data)
    
    # Plot spatial map (lat/lon) - using static matplotlib since Plotly had JS issues
    plot_spatial_map(ds, variable_name, cmap='RdYlBu_r', interactive=False)
    
    # Extract data as list of [lat, lon, value]
    data_list = get_spatial_data_as_list(ds, variable_name, skip_nan=True)
    
    # Sample data if too large (for better web performance)
    if len(data_list) > 100000:
        print(f"Sampling data from {len(data_list):,} to ~100,000 points for web performance...")
        import random
        random.seed(42)
        data_list_web = random.sample(data_list, 100000)
    else:
        data_list_web = data_list
    
    # Show first few entries
    print("\nFirst 5 data points [lat, lon, value]:")
    for row in data_list[:5]:
        print(f"  {row}")
    
    # Export data to HTML file
    print("\n" + "="*50)
    print("Exporting to interactive HTML with world map overlay...")
    print("="*50)
    
    import json
    
    # Convert data to JSON
    data_json = json.dumps(data_list_web)