'''
Script module
'''

from time import time
from map_films.films import get_info_from_user, read_locations, convert_addresses_to_coords,\
get_points_to_put_on_map, create_map


def main() -> None:
    '''
    Creates map of nearest film shooting locations
    '''

    start_time = time()

    user_location, year, fast = get_info_from_user()
    if not user_location or not year:
        return 'Passed arhumants aren\'t good'

    locations = read_locations('data/locations.csv', year, user_location, fast)
    try:
        locations = convert_addresses_to_coords(locations)
    except ValueError:
        return 'Passed arhumants aren\'t good'
    places = get_points_to_put_on_map(locations, user_location)

    file_name = create_map(places, user_location, year)
    print(f'Your map was succesfully created at {file_name}, \
It has taken {round(time() - start_time, 2)}s. to execute')

if __name__ == '__main__':
    main()
