'''
Should be run only once in order to rewrite dataset
'''

from typing import List, Union
import re
import from geopy.geocoders import GoogleV3

def write_dataset(path_to_file: str) -> List[Union[int, str, List[str]]]:
    '''
    Converts info from txt file to List like this [title, year, List[location]]

    TODO: make it work faster (try without re, find out how to pass geopy.exc.GeocoderQueryError)
    '''

    adresses = {}
    with open(path_to_file, encoding='utf-8', errors='ignore') as f, open('outfile.csv', 'a') as outfile:
        for line in f:

            try:
                year = re.search(r'(\d{4})', line).group()
            except AttributeError:
                continue

            # gets title and adress from file
            title = re.search(r'".+"', line).group()[1:-1]
            if '{' in line:
                # adds title of series
                title += re.search(r'{.+}', line).group()
                adress = re.search(r'}.[^()]+', line).group()
            else:
                adress = line.rstrip().split('\t')[-1]
            adress = adress.strip('\t}\n')
            print(adress)

            try:
                outfile.write(f'{year}, {title}, {adresses[adress][0]}, {adresses[adress][1]}\n')
            except KeyError:
                geolocator = GoogleV3(api_key='AIzaSyDOFL0CNeAT7CbmS7hoSI09dQ-R16DKPXI')

                location = geolocator.geocode(adress)
                try:
                    adresses[adress] = location.latitude, location.longitude
                except AttributeError:
                    continue
                outfile.write(f'{year}, {title}, {adresses[adress][0]}, {adresses[adress][1]}\n')

if __name__ == '__main__':
    write_dataset('test_loc.list')
