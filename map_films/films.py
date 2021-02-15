'''
'''

import pandas as pd
import numpy as np
import math
import folium
import folium.plugins as plg
import urllib
import requests
import reverse_geocoder as rg
from multiprocessing.dummy import Pool
from typing import List, Union, Dict, Tuple
from map_films.optimisations import get_adj_states_dict


def get_info_from_user() -> List[Union[List[int], int]]:
    '''
    Gets info from user
    '''

    year = int(input('Please enter a year you would like to have a map for: \n').rstrip())
    location = input('Please enter your location (city or etc.): \n').rstrip()
    fast = input('If you want execute the programme in fast mode, write "y", otherwise, press Enter\n')
    if fast: fast = True
    else: fast = False
    coordinates = get_location(location, {})
    if coordinates == 'nan':
        return False

    return coordinates, year, fast


def read_locations(path_to_file: str, user_year: int, user_coordinates, fast: bool=True) -> List[Union[int, str, List[int]]]:
    '''
    Reads info from csv file with films (written using convert dataset module)
    '''
    
    state = rg.search(user_coordinates)[0]['admin1'] # this returns state name

    with open(path_to_file) as f:
        data = f.readlines()

    # list of adjacent states and the atate itself (where closetst locations will be searched)
    # if none will be found, then there is no locations nearby
    adj_states_set = get_adj_states_dict()[state]
    adj_states_set.add(state)

    cities = set(create_dict_dataset().keys())

    parsed_data = []
    for line in data:
        line = line.rstrip().split(';')

        year = int(line[0])
        title = line[1]

        line[-1] = line[-1].split(', ')
        # if len(line[-1]) means that only state and country is specified, which is not
        # precise enough, therefore we can skeep it
        if len(line[-1]) < 3:
            continue
        # checks whether state is one of adjacent (obviously that the closest ones are somewhere there)
        if line[-1][-2] not in adj_states_set:
            continue
        
        state = line[-1][-2]
        city = line[-1][-3]
        adress = f'{state}, {city}'

        parsed_data.append([year, title, adress])

    if fast:
        parsed_data = [location for location in parsed_data if location[-1] in cities]
    
    df = pd.DataFrame(parsed_data, columns = ['Year', 'Title', 'Address'])

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
    city_locations = [f'{state}, {city}' for state, city in zip(adresses['state_name'].values.tolist(), adresses['city'].values.tolist())]
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
        # distances.append(haversine(films_coord_iter[i], user_coordinates_iter[i]))

    return distances


def get_points_to_put_on_map(films: pd.DataFrame, user_coordinates: List[int]):

    user_coordinates_lst = [(float(user_coordinates[0]), float(user_coordinates[1])) for _ in range(len(films))]
    films_coord_iter = films['Address']
    films_coord_iter = [(float(elm[0]), float(elm[1])) for elm in films_coord_iter]

    films['Diff'] = difference_between_coordinates(films_coord_iter, user_coordinates_lst)
    del films['Year']

    films.sort_values('Diff')
    del films['Diff']
    
    return films.head(10).values.tolist()

def get_income_layer(user_year: int) -> folium.Choropleth:
    '''
    Creates a layer for folium map via folium Choropleth class.
    Shows income per household in each state per year (from range 1984-20??)
    '''

    df = pd.read_csv('data/household_median_income_2017.csv')
    year = str(user_year)
    df = df[['State', year]]
    incomes = df[year].values.tolist()
    incomes = [float('.'.join(income.split(','))) for income in incomes]
    df[year] = incomes

    chor = folium.Choropleth(
        geo_data='data/us_states.json',
        data=df,
        columns=['State', year],
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

    places = [[place[0],(float(place[1][0]), float(place[1][1]))] for place in places]

    # creating first parent layer
    st_map = folium.Map(
        zoom_start=7,
        location=user_location, 
        tiles='stamenwatercolor',
        prefer_canvas=True,
        overlay=True)

    get_income_layer(user_year).add_to(st_map)

    cluster = plg.MarkerCluster().add_to(st_map)
    folium.Marker(location=user_location, popup='Your location', icon=folium.Icon(color='orange')).add_to(st_map)
    for place in places:
        try:
            folium.Marker(location=place[1], popup=place[0], icon=folium.Icon()).add_to(cluster)
        except RecursionError:
            continue
        folium.PolyLine([place[1], user_location], color='red').add_to(st_map)

    file_name = 'map.html'
    st_map.save(file_name)

    return file_name

def main():
    '''
    This is used in terminal
    '''

    from time import time
    start_time = time()
    
    user_location, year, fast = get_info_from_user()
    if not user_location or not year:
        return 'Passes arhumants aren\'t good'

    locations = read_locations('data/locations.csv', year, user_location, fast)
    locations = convert_addresses_to_coords(locations)
    places = get_points_to_put_on_map(locations, user_location)

    file_name = create_map(places, user_location, year)
    print(f'Your map was succesfully created at {file_name}, It has taken {round(time() - start_time, 2)}s. to execute')

if __name__ == '__main__':
    pass