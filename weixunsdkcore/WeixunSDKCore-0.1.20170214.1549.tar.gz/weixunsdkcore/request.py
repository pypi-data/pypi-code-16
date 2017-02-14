#coding=utf-8

import requests
from weixunsdkcore.signature import get_signature_headers

class WeixunRequest(object):
    """
    Weixun Request Base Class
    """
    def __init__(self, service, version=None, function=None, *args, **kwargs):
        """

        :param service:
        :param version:
        :param function:
        """
        self._service = service
        self._version = version
        self._function = function
        self._protocol_type = 'http'
        self._method_type = 'get'
        self._domain_name = ''
        self._query_params = {}
        self._body_params = {}
        self._headers = {}
        self._body = None
        self._signature = ''
        self._files = {}

    """Getters"""

    def get_service(self):
        """

        :return:
        """
        return self._service

    def get_version(self):
        """

        :return:
        """
        return self._version

    def get_function(self):
        """

        :return:
        """
        return self._function

    def get_protocol_type(self):
        """

        :return:
        """
        return self._protocol_type

    def get_method_type(self):
        """

        :return:
        """
        return self._method_type

    def get_domain_name(self):
        """
        return
        :return:
        """
        return self._domain_name

    def get_query_params(self):
        """

        :return:
        """
        return self._query_params

    def get_body_params(self):
        """

        :return:
        """
        return self._body_params

    def get_headers(self):
        """

        :return:
        """
        return self._headers

    def get_files(self):
        """

        :return:
        """
        return self._files

    """Setters"""

    def set_service(self, service):
        """

        :param service:
        :return:
        """
        self._service = service

    def set_version(self, version):
        """

        :param version:
        :return:
        """
        self._version = version

    def set_function(self, function):
        """

        :param function:
        :return:
        """
        self._function = function

    def set_protocol_type(self, protocol_type):
        """

        :param protocol_type:
        :return:
        """
        self._protocol_type = protocol_type

    def set_method_type(self, method_type):
        """

        :param method_type:
        :return:
        """
        self._method_type = method_type

    def set_domain_name(self, domain_name):
        """

        :param domain_name:
        :return:
        """
        self._domain_name = domain_name

    def set_query_params(self, **query_params):
        """

        :param query_params:
        :return:
        """
        self._query_params = query_params

    def set_body_params(self, **body_params):
        """

        :param body_params:
        :return:
        """
        self._body_params = body_params

    def set_headers(self, headers):
        """

        :param headers:
        :return:
        """
        self._headers = headers

    def set_body(self, body):
        """

        :param body:
        :return:
        """
        self._body = body

    def set_files(self, files):
        """

        :param files:
        :return:
        """
        self._files = files

    """Logics"""

    def get_url(self):
        """

        :return:
        """
        return (self.get_protocol_type() +
                '://' + self.get_domain_name() +
                '/api/' + self.get_service() + '/' + self.get_version() + '/' + self.get_function() + '/')

    def add_file_param(self, name, file_path):
        """

        :param self:
        :param file_path:
        :return:
        """
        self._files[name] = open(file_path, 'rb')

    def add_query_param(self, name, value):
        """

        :param name:
        :param value:
        :return:
        """
        self._query_params[name] = value

    def add_body_param(self, name, value):
        """

        :param name:
        :param value:
        :return:
        """
        self._body_params[name] = value

    def add_header(self, name, value):
        """

        :param name:
        :param value:
        :return:
        """
        self._headers[name] = value

    def get_body(self):
        """

        :return:
        """
        if self._body:
            return self._body
        elif self.get_body_params():
            return self.get_body_params()

    def get_method_func(self):
        """

        :return:
        """
        return getattr(requests, self.get_method_type())

    def get_req(self, app_id, app_key):
        """

        :param app_id:
        :param app_key:
        :return:
        """
        # 签名
        query_params = self.get_query_params()
        body_params = self.get_body_params()
        file_params = self.get_files()
        headers = self.get_headers()
        method = self.get_method_type()
        signed_headers = get_signature_headers(query_params, body_params, app_id, app_key, headers, method)
        self.set_headers(signed_headers)
        method_func = self.get_method_func()
        req = method_func(
            url=self.get_url(),
            params=self.get_query_params(),
            headers=self.get_headers(),
            data=self.get_body(),
            files=file_params,
        )
        return req




