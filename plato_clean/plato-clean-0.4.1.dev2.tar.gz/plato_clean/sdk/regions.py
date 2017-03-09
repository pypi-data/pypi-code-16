import json
import requests

####################################
#
# TO BE DONE. TODO
#
####################################


class RegionManager(object):

    def __init__(self, regions_url):
        self.known_regions = {}
        self.url = regions_url
        self.init_regions()

    def init_regions(self):
        res = requests.get(self.url)
        data = json.loads(res.text)['data']
        for region in data['regions']:
            name = region['name']
            endpoint = region['endpoint']
            self.known_regions[name] = endpoint

    def get_endpoint(self, region_name):
        return self.known_regions[region_name]

regions = RegionManager('http://localhost/regions')
