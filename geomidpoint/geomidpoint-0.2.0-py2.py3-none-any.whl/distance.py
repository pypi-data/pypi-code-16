""" Utility methods that can be reused as scope grows """

from math import radians, cos, sin, asin, sqrt, atan2, pi
import googlemaps
from datetime import datetime

EARTH_CIRCUMFERENCE = 6371  # in kilometers

gmaps = googlemaps.Client(key='AIzaSyCkskB_PHpqkN4SelQulTgbi86jWvxyOOg')


def driving_distance(coordinates, midpoint):
    """
    retrieves the driving distance from
    google maps api for a list of coordinates
    """

    # build up the request data
    origins = [(person['Latitude'], person['Longitude']) for person in coordinates]

    # set the destination to the midpoint for each coordinate
    destinations = [(midpoint['Latitude'], midpoint['Longitude'])*len(coordinates)]

    # make the request
    google_result = gmaps.distance_matrix(
        origins=origins,
        destinations=destinations,
        mode='driving',
        departure_time=datetime.now()
    )

    # return the reponse
    return google_result['rows']


def haversine(coordinate1, coordinate2):
    """
    returns the distance between two
    coordinates using the haversine formula
    """

    lon1 = coordinate1['Longitude']
    lat1 = coordinate1['Latitude']
    lon2 = coordinate2['Longitude']
    lat2 = coordinate2['Latitude']

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = EARTH_CIRCUMFERENCE * c
    return distance


def midpoint(coordinates):

    """ calculates the midpoint of a list coordinates """

    if len(coordinates) == 1:
        return coordinates

    x = y = z = 0

    for coordinate in coordinates:
        longitude = radians(coordinate['Longitude'])
        latitude = radians(coordinate['Latitude'])

        x += cos(latitude) * cos(longitude)
        y += cos(latitude) * sin(longitude)
        z += sin(latitude)

        num_coordinates = len(coordinates)

        x = x / num_coordinates
        y = y / num_coordinates
        z = z / num_coordinates

        centralLongitude = atan2(y, x)
        centralSquareRoot = sqrt(x * x + y * y)
        centralLatitude = atan2(z, centralSquareRoot)

        midpoint = {
            'Latitude': centralLatitude * 180 / pi,
            'Longitude': centralLongitude * 180 / pi
        }

    return midpoint
