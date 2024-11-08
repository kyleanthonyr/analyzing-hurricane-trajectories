import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.stats import gaussian_kde
from datetime import datetime

file_path = "data/detailed_storm_data.pkl"
with open(file_path, 'rb') as file:
    storm_data = pickle.load(file)

storm_data['time'] = pd.to_datetime(storm_data['time'])

gulf_coast_bounds = {
    "lat_min": 10.0,
    "lat_max": 35.0,
    "lon_min": -100.0,
    "lon_max": -80.0
}

current_year = datetime.now().year
min_year = current_year - 25
max_year = current_year
init_start_year = min_year
init_end_year = max_year

def get_gulf_storms_data(start_year, end_year):
    storm_data_years = storm_data[(storm_data['time'].dt.year >= start_year) &
                                  (storm_data['time'].dt.year <= end_year)]

    gulf_coast_storms = storm_data_years[
        (storm_data_years['lat'] >= gulf_coast_bounds["lat_min"]) &
        (storm_data_years['lat'] <= gulf_coast_bounds["lat_max"]) &
        (storm_data_years['lon'] >= gulf_coast_bounds["lon_min"]) &
        (storm_data_years['lon'] <= gulf_coast_bounds["lon_max"])
    ]

    return gulf_coast_storms

def plot_density_kde_with_map(start_year, end_year):
    gulf_coast_storms = get_gulf_storms_data(start_year, end_year)
    
    lats = gulf_coast_storms['lat'].values
    lons = gulf_coast_storms['lon'].values
    
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    ax.set_extent([gulf_coast_bounds["lon_min"], gulf_coast_bounds["lon_max"],
                   gulf_coast_bounds["lat_min"], gulf_coast_bounds["lat_max"]])

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')

    x_grid = np.linspace(gulf_coast_bounds["lon_min"], gulf_coast_bounds["lon_max"], 100)
    y_grid = np.linspace(gulf_coast_bounds["lat_min"], gulf_coast_bounds["lat_max"], 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    xy = np.vstack([X.ravel(), Y.ravel()])
    
    kde = gaussian_kde([lons, lats], bw_method=0.1) 
    Z = kde(xy).reshape(X.shape)

    density = ax.pcolormesh(X, Y, Z, cmap="Reds", shading='auto', transform=ccrs.PlateCarree())
    fig.colorbar(density, ax=ax, orientation="vertical", label="Density")

    ax.set_title(f"Storm Occurrence Density in Gulf Coast Region ({start_year}-{end_year})")
    plt.show()

plot_density_kde_with_map(init_start_year, init_end_year)
