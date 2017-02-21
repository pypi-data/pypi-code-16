import os

import requests


IATACODES_API_KEY = os.environ.get('IATACODES_API_KEY')

cities = requests.get("https://iatacodes.org/api/v6/cities?api_key={}".format(
    IATACODES_API_KEY)).json()['response']


default_countries = {
    'paris': 'fr',
    'berlin': 'de'
}


def get_airports(str_city):
    """
    Returns all airport codes of available cities that match the users
    location with their country code.

    :param str_city: The user input.
    :return:         Yields tuples with the airport code and the country code.
    """
    str_city = str_city.lower().strip()

    if ',' in str_city:
        city_part, country_part = map(str.strip, str_city.split(','))
    else:
        city_part = str_city
        country_part = default_countries.get(city_part)

    if len(city_part) == 3:
        try:
            yield city_part.upper(), [city['country_code']
                                      for city in cities
                                      if city['code'].lower() == city_part][0]
            return
        except IndexError:
            pass  # No airport with that code available! Go on.

    for city in cities:
        if (city['name'].lower() == city_part and
                (not country_part or
                 country_part == city['country_code'].lower())):
            yield city['code'], city['country_code']
