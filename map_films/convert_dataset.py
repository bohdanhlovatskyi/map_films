'''
Should be run only once in order to rewrite dataset
'''

from typing import List, Union
import re


def write_dataset(path_to_file: str, write_to_file: str) -> List[Union[int, str, List[str]]]:
    '''
    Converts info from txt file to List like this [title, year, List[location]]
    '''

    with open(path_to_file, encoding='utf-8', errors='ignore') as file:
        data = file.readlines()


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
    Gets year from string
    '''

    try:
        year = re.search(r'(\d{4})', line).group()
    except AttributeError:
        return None

    return year


def get_adress(line: str) -> str:
    '''
    Gets adress from string
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

    # to make it work only for USA
    if 'USA' not in adress:
        return None

    return ', '.join(adress)


def get_title(line: str) -> str:
    '''
    Gets title from string
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
    # rewrites dataset
    write_dataset('data/locations.list', 'data/outfile2.csv')
