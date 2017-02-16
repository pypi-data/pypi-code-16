__author__ = 'lsamaha'

from dervisher.event import Event


class Dervisher(object):

    def __init__(self, name, post):
        self.name = name
        self.post = post

    def start(self, rpm):
        self.post.event(
            Event(event_class='start', event_type='service', subtype='whirl', env='dev', name=self.name))

    def stop(self):
        self.post.event(
            Event(event_class='stop', event_type='service', subtype='whirl', env='dev', name=self.name))

