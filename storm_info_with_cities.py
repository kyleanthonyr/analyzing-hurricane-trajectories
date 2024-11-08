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

current_year = datetime.now().year
min_year = current_year - 25
max_year = current_year

init_start_year = min_year
init_end_year = max_year

def plot_storm_tracks(start_year, end_year):
    storm_data_years = storm_data[(storm_data['time'].dt.year >= start_year) &
                                  (storm_data['time'].dt.year <= end_year)]

    city_count = dict()
    city_intensity = dict()
    city_duration = dict()

    for city_name, city_track in city_data.groupby('City Name'):
        city_count[city_name] = 0
        city_intensity[city_name] = 0
        city_duration[city_name] = 0

    for storm_id, storm_track in storm_data_years.groupby('storm_id'):
        storm_lon = storm_track.iloc[0,6]
        storm_lat = storm_track.iloc[0,5]
        for city_name, city_track in city_data.groupby('City Name'):
            city_lon = city_track.iloc[0,3]
            city_lat = city_track.iloc[0,2]
            if(city_lon-1 < storm_lon and city_lon+1 > storm_lon or
              city_lat-1 < storm_lat and city_lat+1 > storm_lat):
              value = city_count[city_name]
              value+=1
              city_count[city_name] = int(value)
              
              intensity = city_intensity[city_name]
              intensity += storm_track.iloc[0,7]
              city_intensity[city_name] = intensity

              hours = ((storm_track.size / 12) - 1)*6
              time = city_duration[city_name]
              time += hours
              city_duration[city_name] = time
    
    for city_name, city_track in city_data.groupby('City Name'):
        intensity = city_intensity[city_name]
        count = city_count[city_name]
        time = city_duration[city_name]

        if(count != 0):
          averageInt = intensity/count
          city_intensity[city_name] = averageInt

          averageTime = time/count
          city_duration[city_name] = averageTime

    fig = plt.figure(figsize = (12.5, 5))
    plt.barh(city_count.keys(), city_count.values())
    fig.suptitle("number of storms in a 1 Latitude/Longitude distance from a city")
    plt.xlabel("count of storms")
    plt.show()       

    fig = plt.figure(figsize = (12.5, 5))
    plt.barh(city_intensity.keys(), city_intensity.values())
    fig.suptitle("The average intensity of storms over each city")
    plt.xlabel("average intensity")
    plt.show()   

    fig = plt.figure(figsize = (12.5, 5))
    plt.barh(city_duration.keys(), city_duration.values())
    fig.suptitle("average lifespan of hurricanes that go over each city")
    plt.xlabel("average length of storm in hours")
    plt.show()   


plot_storm_tracks(min_year,max_year)