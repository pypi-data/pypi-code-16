import csv
import distance
from operator import itemgetter


class LocationDataSet(object):

    def __init__(self, csv_file):
        self.raw_data = csv.DictReader(csv_file)
        self.midpoint = None
        self.data = None
        self.__clean_data__()

    def __clean_data__(self):
        """ clean data from csv file """
        data_list = list(self.raw_data)

        for row in data_list:
            row['Longitude'] = float(row['Longitude'])
            row['Latitude'] = float(row['Latitude'])

        self.data = data_list

    def build_report(self, is_driving=False):
        """ builds a report using the relevant formula """
        data = self.data
        self.__calculate_midpoint__()

        if is_driving:
            driving_distances = distance.driving_distance(data, self.midpoint)
            for gdistance, person in zip(driving_distances, data):
                result = float(gdistance['elements'][0]['distance']['value'])
                person['Distance'] = "%.2f" % (result / 1000)

        else:
            for person in self.data:
                crow_dist = distance.haversine(person, self.midpoint)
                person['Distance'] = "%.2f" % (crow_dist)

        self.distance_report = sorted(data, key=itemgetter('Distance'))
        return self.distance_report

    def __calculate_midpoint__(self):
        self.midpoint = distance.midpoint(self.data)
        return self.midpoint

    def save(self, filename):
        fieldnames = self.distance_report[0].keys()
        # with open(filename, 'wb') as f:
        writer = csv.DictWriter(filename, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(self.distance_report)
