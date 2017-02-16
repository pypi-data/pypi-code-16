__author__ = 'lsamaha'

import json
import time

class Event(object):

    def __init__(
            self, event_class, event_type, subtype, name, env, uow_uid=None, event_version ='0.1', pretty=False):
        self.event_class = event_class
        self.event_type = event_type
        self.subtype = subtype
        self.name = name
        self.env = env
        self.uow_uid = uow_uid
        self.pretty = pretty
        self.at = int(time.time() * 1000)
        self.event_version = event_version

    def tojson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4 if self.pretty else None)








