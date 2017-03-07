# -*- coding: utf-8 -*-


class UserService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_user(self):
        return self.__client.call("eleme.user.getUser", {})

