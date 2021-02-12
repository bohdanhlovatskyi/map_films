import pandas as pd
import numpy as np
import math
import folium
import urllib
import requests
from multiprocessing.dummy import Pool
from typing import List, Union, Dict
from random import random


def get_info_from_user() -> List[Union[List[int], int]]:
    '''
    Gets info from user
    '''

    year = int(input('Please enter a year you would like to have a map for: \n').rstrip())
    location = list(map(float,
                input('Please enter your location (format: lat, long): \n').rstrip().split(',')))
    return location, year


def read_locations(path_to_file: str, user_year: int) -> List[Union[int, str, List[int]]]:
    '''
    Reads info from csv file with films (written using convert dataset module)
    '''
    
    with open(path_to_file) as f:
        data = f.readlines()

    for idx, line in enumerate(data):
        line = line.rstrip().split('| ')
        data[idx] = [int(line[0]), line[1], line[2]]

    df = pd.DataFrame(data, columns=['Year', 'Title', 'Address'])

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


def crearte_dict_dataset(csv_dv: str) -> Dict[str, List[str]]:
    '''
    '''

    adresses = {}
    with open(csv_dv) as f:
        data = f.readlines()

    for idx, line in enumerate(data):
        line = line.split(',')
        line = [line[0], line[2], line[3]]
        line = [elm.strip('"') for elm in line]
        adresses[line[0]] = (line[1], line[2])
    
    return adresses

def convert_addresses_to_coords(df: pd.DataFrame) -> pd.DataFrame:
    '''
    '''

    adresses_dict = crearte_dict_dataset('data/worldcities.csv')
    locations_to_process = df['Address'].tolist()
    # tried threading to make it wark faster (not really, to be honest)
    with Pool(5) as pool:
        locations_to_process = list(pool.map(
            lambda x: get_location(x, adresses_dict), locations_to_process))

    df['Address'] = locations_to_process
    
    df = df.dropna()

    return df


def difference_between_coordinates(films_coord_iter: List[float], user_coordinates_iter: List[float]):
    '''
    '''

    distances = []
    haversin = lambda x: pow(math.sin(x / 2), 2)
    EARTH_RADIUS = 6371

    trig_expr = 0
    sqrt_expr = 0
    distance = 0
    for i in range(len(films_coord_iter)):
        trig_expr = (haversin(films_coord_iter[i][0] - user_coordinates_iter[i][0]) +\
                math.cos(films_coord_iter[i][0]) * math.cos(user_coordinates_iter[i][0]) *\
                haversin(films_coord_iter[i][1] - user_coordinates_iter[i][1]))
        sqrt_expr = math.sqrt(trig_expr)
        distance = 2 * EARTH_RADIUS * math.asin(sqrt_expr)
        distances.append(distance)

    return distance


def get_points_to_put_on_map(films: pd.DataFrame, user_coordinates: List[int]):
    '''
    TODO: find out how to delete using iloc (delete year column)
    '''

    user_coordinates_lst = [user_coordinates for _ in range(len(films))]
    films_coord_iter = films['Address']
    films_coord_iter = [(float(elm[0]), float(elm[1])) for elm in films_coord_iter]

    films['Diff'] = difference_between_coordinates(films_coord_iter, user_coordinates_lst)
    del films['Year']
    films.sort_values('Diff')
    del films['Diff']
    films = films.head(5)

    return films.values.tolist()


def create_map(places: List[Union[str, List[str]]], user_location: str) -> str:
    '''
    '''

    st_map = folium.Map()

    for place in places:
        loc = tuple(map(lambda x: float(x) + random(), place[-1]))

        st_map.add_child(folium.Marker(location=loc, popup=place[0], icon=folium.Icon()))
    st_map.add_child(folium.Marker(location=user_location, popup='Your location', icon=folium.Icon(color='red')))
    file_name = 'map.html'
    st_map.save(file_name)

    return file_name

def main():
    from time import time
    start_time = time()
    
    user_location, year = get_info_from_user()

    locations = read_locations('data/locations.csv', year)
    # print(locations)

    locations = convert_addresses_to_coords(locations)
    # print(locations)
    places = get_points_to_put_on_map(locations, user_location)
    # print(places)
    file_name = create_map(places, user_location)
    print(f'Your map was succesfully created at {file_name}, It has taken {round(time() - start_time, 2)}s. to execute')
