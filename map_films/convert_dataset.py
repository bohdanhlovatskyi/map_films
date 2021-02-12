'''
Should be run only once in order to rewrite dataset
'''

import re
import requests
import urllib.parse
from functools import lru_cache
from typing import List, Union, Dict


def write_dataset(path_to_file: str) -> List[Union[int, str, List[str]]]:
    '''
    Converts info from txt file to List like this [title, year, List[location]]

    TODO: make it work faster (try without re, find out how to pass geopy.exc.GeocoderQueryError)
    '''

    adresses = crearte_dict_dataset('worldcities.csv')
    with open(path_to_file, encoding='utf-8', errors='ignore') as f:
        data = f.readlines()

    with open('outfile1.csv', 'a') as outfile1:
        for idx, line in enumerate(data):
            print(idx)
            year = get_year(line)
            adress = get_adress(line)
            if not year or not adress:
                continue
            title = get_title(line)
            try:    
                lat, lon = get_location(adress, adresses)
            except TypeError as err:
                continue
            print(f'{year}, {title}, {lat}, {lon}\n')
            outfile1.write(f'{year}, {title}, {lat}, {lon}\n')


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


def get_year(line: str) -> str:
    '''
    '''

    try:
        year = re.search(r'(\d{4})', line).group()
    except AttributeError:
        return None

    return year


def get_adress(line: str) -> str:
    '''
    '''

    if '{' in line:
        adress = re.search(r'}.[^()]+', line).group()
    else:
        adress = line.rstrip().split('\t')[-1]
    adress = adress.strip('\t}\n').split(', ')
    if len(adress) == 3:
        adress = adress[0]
    else:
        try:
            adress = adress[1]
        except IndexError:
            return None

    return adress


def get_title(line: str) -> str:
    '''
    '''

    title = re.search(r'".+"', line).group()[1:-1]
    if '{' in line:
        title += re.search(r'{.+}', line).group()

    return title

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
            adresses[adress] = None
            return None

        adresses[adress] = coords

    return adresses[adress]


if __name__ == '__main__':
    write_dataset('locations.list')
