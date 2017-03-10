import json
from os.path import isfile


class Remotes:
    def __init__(self, list_location):
        self.remotes = self.__parse_list(list_location)

    def __parse_list(self, list_location):
        remote_list = []
        if not isfile(list_location):
            raise Exception('Failed to get remote list from {0}: file not found.'
                            .format(list_location))
        with open(list_location, 'r') as f:
            try:
                remotes_parsed = json.load(f)
                remote_list = remotes_parsed['list']
            except json.JSONDecodeError:
                raise Exception('Failed to read remote list from {0}: syntax error.'
                                .format(list_location))
            except KeyError:
                raise Exception('Invalid remotes file!')
        return remote_list
