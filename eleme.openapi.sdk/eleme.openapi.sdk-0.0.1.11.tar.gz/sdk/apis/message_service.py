# -*- coding: utf-8 -*-


class MessageService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_non_reached_messages(self, app_id):
        return self.__client.call("eleme.message.getNonReachedMessages", {"appId": app_id})

    def get_non_reached_o_messages(self, app_id):
        return self.__client.call("eleme.message.getNonReachedOMessages", {"appId": app_id})

