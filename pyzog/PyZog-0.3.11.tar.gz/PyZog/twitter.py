#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twython import Twython
import PyBird.config as config
from easygui import fileopenbox

__author__ = "LaBatata (Victor Hugo Gomes)"
__version__ = "0.3.11"
__email__ = "labatata101@gmail.com"


class Twitter:

    def __init__(self):
        self.twitter = None

    def tweetar(self):
        self.twitter.update_status(status=input("Twettar: "))

    def tweetar_com_foto(self):
        path = fileopenbox()
        if path:
            foto = open(path, 'rb')
            response = self.twitter.upload_media(media=foto)
            self.twitter.update_status(status=input("Tweet: "),
                                       media_ids=[response['media_id']])
        else:
            return

    def tweetar_com_video(self):
        path = fileopenbox()
        if path:
            video = open(path, 'rb')
            response = self.twitter.upload_video(media=video)
            self.twitter.update_status(status=input("Tweet: "),
                                       media_ids=[response['media_id']])
        else:
            return

    def search(self):
        result = self.twitter.search(q=input("Pesquisar: "), lang='all',
                                     count='50')

        for tweet in result['statuses']:
            print("%s\n [@%s]" % (tweet['user']['name'],
                                  tweet['user']['screen_name']))
            print(">>> %s \n" % tweet['text'])

    def timeline(self):
        time_line = self.twitter.get_home_timeline(count='200')
        for tweet in time_line:
            print("%s \n [@%s]" % (tweet['user']['name'],
                                   tweet['user']['screen_name']))
            print(">>> %s\n" % tweet['text'])

#    @classmethod
    def loga(self):
        key = config.load_conf_file()["keys"]
        self.twitter = Twython(key["consumer_key"],
                               key["consumer_secret"],
                               key["token_key"],
                               key["token_secret"])

#    @classmethod
    def cria_conta(self):
        keys = {"keys": {}}
        keys["keys"]["consumer_key"] = input("Digite sua Consumer Key: ")
        keys["keys"]["consumer_secret"] = input("Digite sua Consumer Secret: ")
        keys["keys"]["token_key"] = input("Digite seu Token Key: ")
        keys["keys"]["token_secret"] = input("Digite seu Token Secret: ")
        config.create_conf_file(keys)
        self.loga()
