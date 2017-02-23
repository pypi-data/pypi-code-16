# -*- coding: utf-8 -*-

import os
import hashlib
import requests

from ant2mvn import logger

log = logger.get_logger(__name__)

def get_files(path, file_extension=""):
    file_pathes = []

    for entry in os.scandir(path):
        if entry.name.endswith(file_extension) and entry.is_file():
            file_pathes.append(entry.path)

    return file_pathes


def sha1(data):
    s1 = hashlib.sha1()
    s1.update(data)
    return s1.hexdigest()


class MavenCentralRepoRestSearchApi(object):
    def __init__(self, name, host, port=80):
        self.name = name
        self.host = host
        self.port = port

        self.rest_search_api = {
            'sha1': 'http://%(host)s:%(port)s/%(api)s' % {
                'host': host,
                'port': str(port),
                'api': 'solrsearch/select'
            }
        }

    def sha1_search(self, sha1, rows=20):
        resp = requests.get(r'%(url)s?q=1:%(sha1)s&rows=%(rows)s&wt=%(wt)s' % {
            'url': self.rest_search_api.get('sha1'),
            'sha1': sha1,
            'rows': rows,
            'wt': 'json'
        })

        log.debug(resp.url)

        return resp.json()


