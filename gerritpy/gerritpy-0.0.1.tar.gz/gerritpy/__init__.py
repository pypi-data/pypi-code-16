#coding=utf-8

import json
import os
import requests
from collections import namedtuple

DEBUG = False


def get_http(url, path, username, password, method="GET"):
    """HTTP Requset"""
    auth = requests.auth.HTTPDigestAuth(username, password)
    url = url +os.sep+"a"+ path

    if DEBUG:
        print "Shell: curl --digest --user '{username}':'{password}' '{url}'"\
            .format(method=method, username=username, password=password, url=url)
    resp = dict(GET=requests.get)[method]
    response = resp(url, auth=auth)

    if response.status_code != requests.codes.ok:
        raise gerritpyerror(response.status_code)
    content = response.content


    if content.startswith(")]}'"):
        content = content.split(")]}'")[1]

        resp_json = json.loads(content)
        if DEBUG:
            print 'Return:', json.dumps(resp_json, indent=4)

        # r = ""
        #
        # print resp_json
        #
        # if isinstance(resp_json, dict):
        #
        #     r = convert(resp_json)
        #
        # elif isinstance(resp_json, list):
        #     r = []
        #     print resp_json
        #     for i in resp_json:
        #         i = convert(i)
        #         r.append(i)
        return resp_json

class gerritpyerror(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return 'ConnectError(status=%d)' % (self.status)

def convert(dictionary):
    """Convert dict to tuple"""
    return namedtuple('GerritDict', dictionary.keys())(**dictionary)