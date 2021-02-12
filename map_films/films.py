import pandas as pd
import re
import math
import folium
from typing import List, Union
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
        line = line.rstrip('\n').split(', ')
        try:
            data[idx] = [int(line[0]), ', '.join(line[1:-2]), (float(line[-2]), float(line[-1]))]
        except ValueError:
            continue

    data = [elm for elm in data if elm[0] == user_year]
    return data

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
        trig_expr = haversin(films_coord_iter[i][0] - user_coordinates_iter[i][0]) +\
                math.cos(films_coord_iter[i][0]) * math.cos(user_coordinates_iter[i][0])\
                * haversin(films_coord_iter[i][1] - user_coordinates_iter[i][1])
        sqrt_expr = math.sqrt(trig_expr)
        distance = 2 * EARTH_RADIUS * math.asin(sqrt_expr)
        distances.append(distance)

    return distance


def get_points_to_put_on_map(films: List[Union[int, str, List[str]]], user_coordinates: List[int]):
    '''
    TODO: find out how to delete using iloc (delete year column)
    '''

    df = pd.DataFrame(films)
    df['User_coordinates'] = [user_coordinates for _ in range(len(films))]
    df['Diff'] = difference_between_coordinates(df.iloc[:, 2], df['User_coordinates'])
    df.sort_values('Diff')
    del df['Diff']
    del df['User_coordinates']
    df = df.head(5)

    return df.values.tolist()


def create_map(places: List[Union[str, List[str]]]) -> str:
    '''
    '''

    st_map = folium.Map()

    for place in places:
        loc = tuple(map(lambda x: x + random(), place[-1]))
        st_map.add_child(folium.Marker(location=loc, popup=place[1], icon=folium.Icon()))
    file_name = 'map.html'
    st_map.save(file_name)

    return file_name

if __name__ == '__main__':
    user_location, year = get_info_from_user()
    locations = read_locations('outfile1.csv', year)
    locations = get_points_to_put_on_map(locations, user_location)
    create_map(locations)

