import pickle
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
from matplotlib.widgets import Button, Slider

data_directory = 'data'
file_path = "data/detailed_storm_data.pkl"

with open(file_path, 'rb') as file:
    storm_data = pickle.load(file)

city_path = "data/cities_with_coordinats.pkl"
with open(city_path, 'rb') as file:
    city_data = pickle.load(file)

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

show_names = False
show_cities = False

def plot_storm_tracks(start_year, end_year):
    ax.clear()
    ax.set_extent([gulf_coast_bounds["lon_min"], gulf_coast_bounds["lon_max"],
                   gulf_coast_bounds["lat_min"], gulf_coast_bounds["lat_max"]])

    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')

    storm_data_years = storm_data[(storm_data['time'].dt.year >= start_year) &
                                  (storm_data['time'].dt.year <= end_year)]

    gulf_coast_storms = storm_data_years[
        (storm_data_years['lat'] >= gulf_coast_bounds["lat_min"]) &
        (storm_data_years['lat'] <= gulf_coast_bounds["lat_max"]) &
        (storm_data_years['lon'] >= gulf_coast_bounds["lon_min"]) &
        (storm_data_years['lon'] <= gulf_coast_bounds["lon_max"])
        ]
    

    if show_cities == True:
        cities_in_area = city_data[
        (city_data['Latitude'] >= gulf_coast_bounds["lat_min"]) &
        (city_data['Latitude'] <= gulf_coast_bounds["lat_max"]) &
        (city_data['Longitude'] >= gulf_coast_bounds["lon_min"]) &
        (city_data['Longitude'] <= gulf_coast_bounds["lon_max"])
        ]

        for city_name, track in cities_in_area.groupby('City Name'):
            ax.plot(track['Longitude']-0.4, track['Latitude']+0.1, marker="*", markersize=5, color="red", alpha=1)
            ax.text(track.iloc[0,3], track.iloc[0,2], city_name, fontsize=5, color='black')

    storms = []

    for storm_id, track in gulf_coast_storms.groupby('storm_id'):
        
        
        if storm_id not in storms:
            storms.append(storm_id)
        if show_names == True:            
            ax.text(track.iloc[0,6]+0.2, track.iloc[0,5]+0.1, str(track.iloc[0,11]+" "+track.iloc[0,10]), fontsize=5, color='black')
            
        ax.plot(track['lon'], track['lat'], marker='o', markersize=2, linestyle='-', alpha=0.5)

    ax.set_title(f"Storm Tracks from {start_year} to {end_year} (Gulf Coast Region)")

    plt.draw()

fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
fig.subplots_adjust(left=0.1, bottom=0.35)
plot_storm_tracks(init_start_year, init_end_year)

ax_start_year = fig.add_axes([0.25, 0.15, 0.65, 0.03])
start_year_slider = Slider(
    ax=ax_start_year,
    label="Start Year",
    valmin=min_year,
    valmax=max_year,
    valinit=init_start_year,
    valstep=1
)

ax_end_year = fig.add_axes([0.25, 0.1, 0.65, 0.03])
end_year_slider = Slider(
    ax=ax_end_year,
    label="End Year",
    valmin=min_year,
    valmax=max_year,
    valinit=init_end_year,
    valstep=1
)

def update(val):
    start_year = int(start_year_slider.val)
    end_year = int(end_year_slider.val)

    if start_year > end_year:
        #start_year = end_year
        #start_year_slider.set_val(start_year)
        end_year=start_year
        end_year_slider.set_val(end_year)
        

    plot_storm_tracks(start_year, end_year)

start_year_slider.on_changed(update)
end_year_slider.on_changed(update)

resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
reset_button = Button(resetax, 'Reset', hovercolor='0.975')

cityax = fig.add_axes([0.675, 0.025, 0.1, 0.04])
cities_button = Button(cityax, 'Show Cities', hovercolor='0.975')

storm_names_ax = fig.add_axes([0.525, 0.025, 0.125, 0.04])
names_button = Button(storm_names_ax, 'Show Storm Info', hovercolor='0.975')

def reset(event):
    start_year_slider.reset()
    end_year_slider.reset()

def show_cities(event):
    global show_cities
    
    if show_cities == True:
        show_cities = False
    else:
        show_cities = True

    start_year = int(start_year_slider.val)
    end_year = int(end_year_slider.val)
    
    if start_year > end_year:
        start_year = end_year
        start_year_slider.set_val(start_year)

    plot_storm_tracks(start_year, end_year)
    
def show_storm_names(event):
    global show_names

    if show_names == True:
        show_names = False
    else:
        show_names = True
    
    start_year = int(start_year_slider.val)
    end_year = int(end_year_slider.val)
    
    if start_year > end_year:
        start_year = end_year
        start_year_slider.set_val(start_year)

    plot_storm_tracks(start_year, end_year)

def write_storm_info():
    file = open("storm_info.txt", "w")
    
    storm_data_years = storm_data[(storm_data['time'].dt.year >= min_year) &
                                  (storm_data['time'].dt.year <= max_year)]

    gulf_coast_storms = storm_data_years[
        (storm_data_years['lat'] >= gulf_coast_bounds["lat_min"]) &
        (storm_data_years['lat'] <= gulf_coast_bounds["lat_max"]) &
        (storm_data_years['lon'] >= gulf_coast_bounds["lon_min"]) &
        (storm_data_years['lon'] <= gulf_coast_bounds["lon_max"])
        ]

    for storm_id, track in gulf_coast_storms.groupby('storm_id'):
        minInt = str(int(min(track['vmax'])))
        maxInt = str(int(max(track['vmax'])))
        avgInt = sum(track['vmax']) / track['vmax'].size
        avgInt = "{:.2f}".format(avgInt)

        date = track.iloc[0,1]
        date = str(date)
        #print(date)
    
        hours = str(int(((track.size / 12) - 1)*6))
            
        huricane_info = str(track.iloc[0,11]+" "+track.iloc[0,10]+" "+hours+" hours\n"+
                            "minimum intensity "+minInt+" maximum intensity "+maxInt+" average intensity "+avgInt+"\n"+
                            date+"\n\n"
                            )

        file.write(huricane_info)
        

    file.close()


reset_button.on_clicked(reset)
cities_button.on_clicked(show_cities)
names_button.on_clicked(show_storm_names)

write_storm_info()

plt.show()