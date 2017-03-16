import os

import yaml


class Config(object):
    def __init__(self):
        settings_path = os.path.dirname(os.path.realpath(__file__))+'/settings.yaml'
        try:
            with open(settings_path, 'r') as file:
                settings = yaml.load(file)
            self.cassandra = Cassandra(**settings['cassandra'])
            self.hosts = Hosts(**settings['hosts'])
        except Exception:
            print('no settings file found in path: {}'.format(settings_path))


class Cassandra(object):
    def __init__(self, port, keyspace, table, contact_points, datacenter):
        self.port = port
        self.keyspace = keyspace
        self.table = table
        self.contact_points = contact_points
        self.datacenter = datacenter


class Hosts(object):
    def __init__(self, hostnames, services):
        self.hostnames = hostnames
        self.services = services
