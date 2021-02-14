import pandas as pd
import numpy as np
import math
import folium
import urllib
import requests
from multiprocessing.dummy import Pool
from typing import List, Union, Dict, Tuple
from random import random


def get_info_from_user() -> List[Union[List[int], int]]:
    '''
    Gets info from user
    '''

    year = int(input('Please enter a year you would like to have a map for: \n').rstrip())
    location = input('Please enter your location (city or etc.): \n').rstrip()
    coordinates = get_location(location, {})
    if coordinates == 'nan':
        return False
    print('Wait for your map!')
    
    return coordinates, year


def read_locations(path_to_file: str, user_year: int) -> List[Union[int, str, List[int]]]:
    '''
    Reads info from csv file with films (written using convert dataset module)
    '''
    
    
    with open(path_to_file) as f:
        data = f.readlines()

    for idx, line in enumerate(data):
        line = line.rstrip().split(';')
        line[0] = int(line[0])
        data[idx] = line


    df = pd.DataFrame(data)
    df = df.drop(df.columns[3:], axis=1)
    df.columns = ['Year', 'Title', 'Address']

    return df[df['Year'] == user_year]


def get_location(adress: str, adresses: Dict[str, str]) -> List[str]:
    '''
    '''

    try:
        return adresses[adress]
    except KeyError:
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(adress) +'?format=json'
        response = requests.get(url).json()
        try:
            coords = response[0]["lat"], response[0]["lon"]
        except IndexError:
            adresses[adress] = np.nan
            return np.nan

        adresses[adress] = coords

    return adresses[adress]


def create_dict_dataset() -> Dict[str, List[str]]:
    '''
    '''

    adresses = pd.read_csv('data/uscities.csv')
    adresses = adresses[['city', 'state_name', 'lat', 'lng']]
    city_locations = adresses['city'].values.tolist()
    coordinates = [(float(coord[0]), float(coord[1])) for coord in \
                    zip(adresses['lat'].values.tolist(), adresses['lng'].values.tolist())]
    adresses = {location: coordinate for location, coordinate in zip(city_locations, coordinates)}

    return adresses

def convert_addresses_to_coords(df: pd.DataFrame) -> pd.DataFrame:
    '''
    '''

    adresses_dict = create_dict_dataset()
    locations_to_process = df['Address'].tolist()
    # tried threading to make it wark faster (not really, to be honest)
    with Pool(5) as pool:
        locations_to_process = list(pool.map(
            lambda x: get_location(x, adresses_dict), locations_to_process))

    df['Address'] = locations_to_process

    return df.dropna()


def difference_between_coordinates(films_coord_iter: List[float], user_coordinates_iter: List[float]):
    '''
    '''

    distances = []
    haversin = lambda x: pow(math.sin(x / 2), 2)
    EARTH_RADIUS = 6371

    trig_expr = sqrt_expr = distance = 0
    for i in range(len(films_coord_iter)):
        trig_expr = (haversin(films_coord_iter[i][0] - user_coordinates_iter[i][0]) +\
                math.cos(films_coord_iter[i][0]) * math.cos(user_coordinates_iter[i][0]) *\
                haversin(films_coord_iter[i][1] - user_coordinates_iter[i][1]))
        sqrt_expr = math.sqrt(trig_expr)
        distance = 2 * EARTH_RADIUS * math.asin(sqrt_expr)
        distances.append(distance)

    return distances


def get_points_to_put_on_map(films: pd.DataFrame, user_coordinates: List[int]):

    user_coordinates_lst = [(float(user_coordinates[0]), float(user_coordinates[1])) for _ in range(len(films))]
    films_coord_iter = films['Address']
    films_coord_iter = [(float(elm[0]), float(elm[1])) for elm in films_coord_iter]

    films['Diff'] = difference_between_coordinates(films_coord_iter, user_coordinates_lst)
    films.sort_values('Diff')
    films = films.drop(['Diff', 'Year'], axis=1)

    return films.head(4).values.tolist()

def get_income_layer(user_year):

    df = pd.read_csv('data/household_median_income_2017.csv')
    df = df[['State', str(user_year)]]
    incomes = df[str(user_year)].values.tolist()
    incomes = [float('.'.join(income.split(','))) for income in incomes]
    df[str(user_year)] = incomes

    chor = folium.Choropleth(
        geo_data='data/us_states.json',
        data=df,
        columns=['State', str(user_year)],
        key_on='feature.properties.name',
        fill_color ='YlGnBu',
        fill_opacity = 0.7,
        line_opacity = 0.2,
        legend_name = "Income per house",
        nan_fill_color='white')

    return chor


def create_map(places: List[Union[str, List[str]]], user_location: Tuple[str], user_year) -> str:
    '''
    Creates folium map, which displays 5 closets film shooting locations to user

    Args : list of locations (title, its coordinated)
           user location: tuple with coordinates (str)

    Returns file name.
    '''

    places = [(place[0], tuple(map(lambda x: float(x) + random(), place[-1]))) for place in places]
    # creating first parent layer
    st_map = folium.Map(
        zoom_start=7,
        location=user_location, 
        tiles='stamenwatercolor',
        prefer_canvas=True,
        overlay=True)
    # folium.TileLayer(tiles='http://tile.stamen.com/watercolor/{z}/{x}/{y}.jpg', attr='toner-wc', overlay=False).add_to(st_map)

    folium.TileLayer("Stamen Toner").add_to(st_map)

    get_income_layer(user_year).add_to(st_map)
   
    popups_layer = folium.FeatureGroup()
    user_loc = folium.Marker(location=user_location, popup='Your location', icon=folium.Icon(color='orange'))
    popups_layer.add_child(user_loc)
    for place in places:
        popups_layer.add_child(folium.Marker(location=place[1], popup=place[0], icon=folium.Icon()))
        folium.PolyLine([place[1], user_location], color='red').add_to(st_map)

    # merging data layers
    popups_layer.add_to(st_map)

    file_name = 'map.html'
    st_map.save(file_name)

    return file_name

def main():
    '''
    This is used in terminal
    '''

    from time import time
    start_time = time()
    
    user_location, year = get_info_from_user()
    if not user_location or not year:
        return 'Passes arhumants aren\'t good'

    locations = read_locations('data/locations.csv', year)
    locations = convert_addresses_to_coords(locations)
    places = get_points_to_put_on_map(locations, user_location)

    file_name = create_map(places, user_location, year)
    print(f'Your map was succesfully created at {file_name}, It has taken {round(time() - start_time, 2)}s. to execute')

if __name__ == '__main__':
    pass