"""

Copyright (C) 2015-2016 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

originally added by Catherine Holloway
"""

# !/usr/bin/env python
from requests import session
try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin
from configparser import ConfigParser
from datetime import datetime
#from gateway_helpers import get_headers
from os.path import join
import json
from time import sleep, time

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
CONFIG_URL = 'https://' + COMMON_SETTINGS['DOMAIN']
HEALTH_SEND_TIME = 60 * 60
CONFIG_FETCH_TIME = 1


def get_headers(content_type='application/json'):
    headers = {'Content-type': content_type,
               'gateway-auth-token': CLIENT_SETTINGS['GATEWAY_AUTH_TOKEN']}
    return headers


def url_go(path):
    return urljoin(CONFIG_URL, path)


class CoroutineGateway(object):
    def __init__(self):
        # store all incoming tests in a dict
        self.test_order = {}
        self.headers = get_headers()
        self.session = session()
        self.companyname = COMMON_SETTINGS['COMPANYNAME'].replace(" ", "")
        self.health_url = url_go(join("testplansummary", self.companyname,
                                      COMMON_SETTINGS['HARDWARENAME']))
        self.log_url = url_go(join("nuc_logs", self.companyname,
                                   COMMON_SETTINGS['HARDWARENAME']))
        # instrument name comes from the child object
        self.instrument_name = None
        self.config_form_url = url_go("schemaform")
        # the expected parts for each instrument
        self.config_parts = []
        # uninitialized until "run" is hit on the server's front end
        self.test_run_id = None
        self.angular_form = {}

    def get_health(self):
        print("health url", self.health_url)
        response = self.session.get(self.health_url, headers=self.headers)
        assert response.status_code == 200
        response = response.json()
        assert "test_run" in response.keys()
        if response["test_run"] is None:
            return None
        else:
            if response["config"] == {}:
                return None
            if response["config"]["config_excerpt"] == "":
                return None
            if response["test_run"] is None:
                return None
            out_dict = response["config"]["config_excerpt"]
            out_dict["test_run_id"] = response["test_run"]["id"]
            print("got new test run id:", out_dict["test_run_id"], out_dict.keys(), out_dict["name"])
            return out_dict

    def post_config_form(self):
        _data = self.angular_form
        _data["instrument_type"] = self.instrument_name
        print("instrument type is: ", self.instrument_name)
        response = self.session.post(self.config_form_url,
                                     headers=self.headers,
                                     data=json.dumps(_data))
        assert response.status_code == 200

    def post_health(self):
        _data = {"instruments": [self.instrument_name],
                 "gateway": COMMON_SETTINGS['HARDWARENAME'],
                 "software": COMMON_SETTINGS['SOFTWARE']}
        print("posting health, ", self.health_url)
        response = self.session.post(self.health_url, headers=self.headers,
                                     data=json.dumps(_data))
        assert response.status_code == 200

    def post_log(self, message):
        data = {"message": message, "time": datetime.now().isoformat() }
        response = self.session.post(self.log_url,
                                     data=json.dumps(data, ensure_ascii=True),
                                     headers=self.headers)
        assert response.status_code == 200

    def health_thread(self):
        self.last_post = 0
        self.last_get = 0
        while True:
            sleep(CONFIG_FETCH_TIME)
            if time() - self.last_post > HEALTH_SEND_TIME:
                 self.last_post = time() 
                 self.post_health()
                 self.post_config_form()
            if time() - self.last_get > CONFIG_FETCH_TIME:
                 config = self.get_health()
                 if config is not None:
                     self.test_order = config

