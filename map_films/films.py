import pandas as pd
import re
import folium
from typing import List, Union


def get_info_from_user() -> List[Union[List[int], int]]:
    '''
    Gets info from user
    '''

    year = int(input('Please enter a year you would like to have a map for: \n').rstrip())
    location = list(map(float,
                input('Please enter your location (format: lat, long): \n').rstrip().split(',')))
    return location, year

def read_locations(path_to_file: str) -> List[Union[int, str, List[int]]]:
    '''
    Reads info from csv file with films (written using convert dataset module)
    '''
    
    pass

def difference_between_coordinates(films_coord_iter: List[int], user_coordinates_iter: List[int]):
    '''
    TODO: should be rewritten (there is how in the task)
    '''

    pass


def get_points_to_put_on_map(films: List[Union[int, str, List[str]]], user_coordinates: List[int]):
    '''
    TODO: find out how to delete using iloc (delete year column)
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
        # TODO: change this, after I channge get_points_to_put_on_map
        st_map.add_child(folium.Marker(location=place[-1], popup=place[1], icon=folium.Icon()))
    file_name = 'map.html'
    st_map.save(file_name)
    return file_name

if __name__ == '__main__':
    pass
