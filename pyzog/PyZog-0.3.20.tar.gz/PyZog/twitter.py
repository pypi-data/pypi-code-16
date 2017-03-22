#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twython import Twython, TwythonError
from .config import load_conf_file, create_conf_file
from easygui import fileopenbox

__author__ = "LaBatata (Victor Hugo Gomes Nascimento)"
__version__ = "0.3.20"
__email__ = "labatata101@gmail.com"


class Twitter:

    def __init__(self):
        self.twitter = None

    def get_user_id(self, screen_name):
        user_id = self.twitter.lookup_user(screen_name=screen_name)
        if user_id["code"] == 17:
            return "O usuario não existe."
        return user_id["id"]

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
            print("%s [@%s]" % (tweet['user']['name'],
                                tweet['user']['screen_name']))
            print(">>> %s \n" % tweet['text'])

    def timeline(self):
        time_line = self.twitter.get_home_timeline(count='200')
        for tweet in time_line:
            print("%s [@%s]" % (tweet['user']['name'],
                                tweet['user']['screen_name']))
            print("- %s\n" % tweet['text'])

    def get_user_information(self):
        info = self.twitter.verify_credentials()
        informations = {
            "name": info['name'],
            "screen_name": info['screen_name'],
            "followers": info['followers_count'],
            "following": info['friends_count'],
            "desc": info['description'],
            "fav": info['favourites_count'],
            "tweets": info['statuses_count']
        }
        return informations

    def get_direct_msg(self):
        from pprint import pprint
        get_list = self.twitter.get_direct_messages(count=20)
        for i in get_list:
            pprint(i)

    def get_home_timeline(self):
        """
        Get your own tweets
        """
        name = self.get_user_information()["screen_name"]
        timeline = self.twitter.get_user_timeline(count=200, screen_name=name)
        for tweet in timeline:
            print("[@{}]\n{}\n".format(name, tweet["text"]))

    def send_direct_msg(self):
        try:
            print("=========== Enviar Direct Msg ===========")
            name = input("Digite a @")
            text = input("-> ")
            self.twitter.send_direct_message(screen_name=name, text=text)
        except TwythonError as e:
            print("O usuario não existe: %s" % e)

    def loga(self):
        key = load_conf_file()["keys"]
        self.twitter = Twython(key["consumer_key"],
                               key["consumer_secret"],
                               key["token_key"],
                               key["token_secret"])

    def cria_conta(self):
        keys = {"keys": {}}
        keys["keys"]["consumer_key"] = input("Digite sua Consumer Key: ")
        keys["keys"]["consumer_secret"] = input("Digite sua Consumer Secret: ")
        keys["keys"]["token_key"] = input("Digite seu Token Key: ")
        keys["keys"]["token_secret"] = input("Digite seu Token Secret: ")
        create_conf_file(keys)
        self.loga()
