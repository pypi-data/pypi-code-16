#coding=utf-8

import time

class WeixunClient(object):
    """
    Weixun Service Client
    """
    def __init__(self, app_id, app_key, auto_retry=True, max_retry_time=3, user_agent=None):
        """
        初始化
        :param app_id:
        :param app_key:
        :param auto_retry:
        :param max_retry_time:
        :param user_agent:
        """
        self._app_id = app_id
        self._app_key = app_key
        self._auto_retry = auto_retry
        self._max_retry_time = max_retry_time
        self._user_agent = user_agent

    def get_app_id(self):
        """
        获取AppID
        :return:
        """
        return self._app_id

    def get_app_key(self):
        """
        获取AppKey
        :return:
        """
        return self._app_key

    def is_auto_retry(self):
        """
        :return:Boolean
        """
        return self._auto_retry

    def get_max_retry_time(self):
        """

        :return:
        """
        return self._max_retry_time

    def get_user_agent(self):
        """

        :return:
        """
        return self._user_agent

    """Setters"""

    def set_app_id(self, app_id):
        """

        :return:
        """
        self._app_id = app_id

    def set_app_key(self, app_key):
        """

        :return:
        """
        self._app_key = app_key

    def set_auto_retry(self, flag):
        """
        :return:Boolean
        """
        self._auto_retry = flag

    def set_max_retry_time(self, max_retry_time):
        """

        :return:
        """
        self._max_retry_time = max_retry_time

    def set_user_agent(self, user_agent):
        """

        :return:
        """
        self._user_agent = user_agent

    """Logics"""

    def do_request(self, request_obj):
        return request_obj.get_req(app_id=self.get_app_id(), app_key=self.get_app_key())


