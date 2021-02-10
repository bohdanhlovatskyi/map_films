from map_films import films

if __name__ == '__main__':
    user_coordinates, user_year = films.get_info_from_user()
    films_df = films.get_films('test_loc.list', user_year)
    places = films.get_points_to_put_on_map(films_df, user_coordinates)
    print(f'Map was successfully created, it was sawed as {films.create_map(places)}')