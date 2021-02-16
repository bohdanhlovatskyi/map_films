'''
Contains function that make the main module work faster
Generally drops all the not adjacent states and
creates dict of city, state : coordinates
'''

from typing import Dict, Tuple, Set
import pandas as pd

def adjacent_states() -> Dict[str, Set[str]]:
    '''
    Creates dict, where for each state id are specified its adjacent states' ids
    '''

    with open('data/adjacent_states.csv') as file:
        data = file.readlines()

    adj_states = {}
    for idx, line in enumerate(data):
        line = line.rstrip().split(',')
        adj_states.setdefault(line[0], set()).add(line[1])

    return adj_states


def map_stats() -> Dict[str, str]:
    '''
    Maps states' ids to states' names
    '''

    with open('data/id_state_mapping.csv') as file:
        data = file.readlines()

    for idx, line in enumerate(data):
        line = line.rstrip().split(',')
        data[idx] = [elm.strip('"') for elm in line]


    return {line[1]: line[0]  for line in data}

def convert_dict(adj_states: Dict[str, Set[str]], map_lst: Dict[str, str]) ->\
                Dict[str, Set[str]]:
    '''
    Maps states' ids to states' names in dict of adjacent states
    '''

    mapped_dict = {}
    for key in adj_states:
        mapped_dict[map_lst[key]] = {map_lst[elm] for elm in adj_states[key]}

    return mapped_dict


def get_adj_states_dict() -> Dict[str, Set[str]]:
    '''
    Creates dict, where for each state name are specified its adjacent states
    '''

    adj_dict = adjacent_states()
    map_lst = map_stats()

    return convert_dict(adj_dict, map_lst)


def create_dict_dataset() -> Dict[str, Tuple[int]]:
    '''
    Creates dict dataset city, state: (coordinates) for optimisation
    '''

    adresses = pd.read_csv('data/uscities.csv')
    adresses = adresses[['city', 'state_name', 'lat', 'lng']]
    city_locations = [f'{state}, {city}' for state, city in
                     zip(adresses['state_name'].values.tolist(), adresses['city'].values.tolist())]
    coordinates = [(float(coord[0]), float(coord[1])) for coord in \
                    zip(adresses['lat'].values.tolist(), adresses['lng'].values.tolist())]
    adresses = {location: coordinate for location, coordinate in zip(city_locations, coordinates)}

    return adresses
