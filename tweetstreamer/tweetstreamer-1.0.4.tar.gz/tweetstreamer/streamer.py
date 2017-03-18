# -*- coding: utf-8 -*-

from tweepy import API, OAuthHandler, StreamListener
from tweepy.streaming import Stream

class Listener(StreamListener):
    def __init__(self, api, on_status, on_error, on_timeout):
        self.api = api
        self.on_status = on_status
        self.on_error = on_error
        self.on_timeout = on_timeout

def auth(consumer_key, consumer_secret, access_key, access_secret):
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return {
        'api': API(auth),
        'auth': auth
    }

def listen(connection, track, on_status, on_error, on_timeout, on_disconnect):
    listener = Listener(connection['api'], on_status, on_error, on_timeout)
    stream = Stream(connection['auth'], listener)
    try:
        stream.filter(track=track)
    except Exception as e:
        print e
        on_disconnect(e)
        stream.disconnect()
