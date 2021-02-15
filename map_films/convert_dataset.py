'''
Should be run only once in order to rewrite dataset
'''

import re
import requests
import urllib
from typing import List, Union, Dict


def write_dataset(path_to_file: str, write_to_file: str) -> List[Union[int, str, List[str]]]:
    '''
    Converts info from txt file to List like this [title, year, List[location]]

    TODO: make it work faster (try without re, find out how to pass geopy.exc.GeocoderQueryError)
    '''

    with open(path_to_file, encoding='utf-8', errors='ignore') as f:
        data = f.readlines()

    
    with open(write_to_file, 'a') as outfile:
        for idx, line in enumerate(data):
            print(idx)
            year = get_year(line)
            adress = get_adress(line)
            title = get_title(line)
            if not year or not adress or not title:
                continue
            # print(f'{year}, {title}, {adress}\n')
            outfile.write(f'{year};{title};{adress}\n')


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
        try:
            adress = re.search(r'}.[^()]+', line).group()
        except AttributeError:
            return None
    else:
        try:
            adress = line.rstrip().split('\t')[-1]
        except IndexError:
            return None
    adress = adress.strip('\t}\n').split(', ')
    # if len(adress) == 3:
        # adress = adress[0]
    # else:
        # try:
            # adress = adress[1]
        # except IndexError:
            # return None

    if 'USA' not in adress:
        return None

    return ', '.join(adress)


def get_title(line: str) -> str:
    '''
    '''

    try:
        title = re.search(r'".+"', line).group()[1:-1]
    except AttributeError:
        return None
    if '{' in line:
        try:
            title += re.search(r'{.+}', line).group()
        except AttributeError:
            return None

    return title


if __name__ == '__main__':
    write_dataset('data/locations.list', 'data/outfile2.csv')
