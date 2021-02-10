import pandas as pd
import re
import folium
import requests
import urllib.parse
from typing import List, Union


def get_info_from_user() -> List[Union[List[int], int]]:
    '''
    Gets info from user
    '''

    year = int(input('Please enter a year you would like to have a map for: \n').rstrip())
    location = list(map(float,
                input('Please enter your location (format: lat, long): \n').rstrip().split(',')))
    return location, year

def get_films(path_to_file: str, user_year: int) -> List[Union[int, str, List[str]]]:
    '''
    Converts info from txt file to List like this [name, year, List[location]]
    '''

    with open(path_to_file, encoding='utf-8', errors='ignore') as f:
        data = f.readlines()

    for idx, line in enumerate(data):
        try:
            year = int(re.search(r'(\d{4})', line).group())
        except AttributeError:
            data[idx] = []
            continue
        if year != user_year:
            data[idx] = []
            continue
        title = re.search(r'".+"', line).group()[1:-1]
        if '{' in line:
            title += re.search(r'{.+}', line).group()
            adress = re.search(r'}.[^()]+', line).group().lstrip('}').rstrip()
            adress = adress.replace('\t', '')
        else:
            adress = line.rstrip().split('\t')[-1]
        try:
            # this is where a lot of films are skipped, can be improved, I guess
            # tha's also a place, which takes a lot of time. No, really, a lot.
            #
            # there is sense to run this one time and then safe this maybe
            adress = convert_to_coordinated(adress)
            data[idx] = (year, title, adress)
        except IndexError:
            data[idx] = []
            continue

    return [elm for elm in data if elm]

def convert_to_coordinated(place: List[str]) -> List[int]:
    '''
    '''

    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(place) +'?format=json'
    response = requests.get(url).json()

    return [float(response[0]["lat"]), float(response[0]["lon"])]


def difference_between_coordinates(films_coord_iter: List[int], user_coordinates_iter: List[int]):

    iterable = zip(films_coord_iter, user_coordinates_iter)
    diffs = []
    for films_coord, user_coordinates in iterable:
        diff_in_lon = (abs(films_coord[0]) + abs(user_coordinates[0])) / 2
        diff_in_len = (abs(films_coord[1]) + abs(user_coordinates[1])) / 2
        diff = round(diff_in_len + diff_in_lon, 2)
        diffs.append(diff)

    return diffs


def get_points_to_put_on_map(films: List[Union[int, str, List[str]]], user_coordinates: List[int]):
    '''
    '''

    df = pd.DataFrame(films)
    df['User_coordinates'] = [user_coordinates for _ in range(len(films))]
    df['Diff'] = difference_between_coordinates(df.iloc[:, 2], df['User_coordinates'])
    df.sort_values('Diff').head(10)
    del df['Diff']
    del df['User_coordinates']
    
    return df.values.tolist()


def create_map(places: List[Union[str, List[str]]]) -> str:
    '''
    '''

    st_map = folium.Map()

    for place in places:
        st_map.add_child(folium.Marker(location=place[-1], popup=place[1], icon=folium.Icon()))
    file_name = 'map.html'
    st_map.save(file_name)
    return file_name
