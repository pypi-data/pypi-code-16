"""

Copyright (C) 2015-2016 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

originally added by Catherine Holloway
"""

#!/usr/bin/env python
import sys
from os.path import join, dirname, abspath
from configparser import ConfigParser
# TODO: change instruments to a package to avoid this nonsense
sys.path.append(join(dirname(abspath(__file__)), "device_drivers"))
from time import sleep
import asyncio
from xtend import Xtend
from tek import GOMDO4104
from agilent import GOU2001A
from requests import session
from gateway_helpers import get_headers
from coroutine_gateway import CoroutineGateway

CONFIG_FETCH_TIME = 0.1

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
CONFIG_URL = 'https://' + COMMON_SETTINGS['DOMAIN']


def test_api():
    xg = XtendGateway(power_meter=CLIENT_SETTINGS["AGILENT_U2000A_ADDRESS"],
                      scope=CLIENT_SETTINGS["TEK_MDO4104_ADDRESS"],
                      xtend=CLIENT_SETTINGS["XTEND_ADDRESS"])


def run_gateway():
    xg = XtendGateway(power_meter=CLIENT_SETTINGS["AGILENT_U2000A_ADDRESS"],
                      scope=CLIENT_SETTINGS["TEK_MDO4104_ADDRESS"],
                      xtend=CLIENT_SETTINGS["XTEND_ADDRESS"])
    loop = asyncio.get_event_loop()
    tasks = [
        xg.fetch_config(),
        xg.run_test()]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


#def json_to_attr(to_set, ):



class XtendGateway(CoroutineGateway):
    def __init__(self, power_meter, scope, xtend):
        super(XtendGateway, self).__init__()
        self.xt = Xtend(xtend)
        self.pm = GOU2001A(power_meter)
        self.scope = GOMDO4104(scope)
        self.session = session()
        self.headers = get_headers()
        self.pm._interface.timeout = 10
        self.pm.utility.reset()
        self.scope.utility.reset()
        sleep(3)
        for ch in self.scope.channels:
            ch.enabled = False


#    def set_config(self):




if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv.append("")
    if sys.argv[1] == "-t":
        test_api()
    else:
        run_gateway()
