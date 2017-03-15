import requests
import json
import xml.etree.ElementTree as ET

import logging
log = logging.getLogger("XMLTestLogger")


# Class to connect to remote server
class Dialer:

    def __init__(self, url, method, request):
        self.url = url
        self.method = method
        self.headers = {}
        self.cookies = {}
        self.data = {}
        self.__extract_from_request__(request)
        log.debug(" DIALER: " + self.__to_string__())

    # Method for testing
    def to_string(self):
        return self.url + " " + self.method + " " + \
            str(self.headers) + " " + str(self.cookies)

    def __to_string__(self):
        return "\n    URL: " + self.url \
            + "\n    Method:" + self.method \
            + "\n    Headers:" + str(self.headers) \
            + "\n    Cookies: " + str(self.cookies)

    def __extract_from_request__(self, request_property):
        if 'header' in request_property.keys():
            self.headers = self.__extract_header__(
                request_property['header'])

        if 'cookie' in request_property.keys():
            self.cookies = self.__extract_cookie__(
                request_property['cookie'])

        if 'data' in request_property.keys():
            self.data = self.__extract_data__(
                request_property['data'])

    def __extract_header__(self, header_str):
        headers = {}
        for h in header_str.split(","):
            kv = h.split(':')
            headers[kv[0].strip()] = kv[1].strip()
        return headers

    def __extract_cookie__(self, cookie_str):
        cookies = {}
        for h in cookie_str.split(","):
            kv = h.split(':')
            cookies[kv[0].strip()] = kv[1].strip()
        return cookies

    def __extract_data__(self, data_str):
        data = {}
        for d in data_str.split(","):
            kv = d.split(":")
            data[kv[0].strip()] = kv[1].strip()
        return data

    # Method used for testing
    def dial_and_parse_json(self):
        res_text = self.dial()
        return json.loads(res_text)

    def dial_and_parse_xml(self):
        res_text = self.dial()
        return ET.fromstring(res_text)

    def dial(self):
        if self.method == "GET" or self.method == "get":
            response = requests.get(self.url, headers=self.headers,
                                    cookies=self.cookies)

            if response.status_code != 200:
                raise Exception("Error in API response. status_code: " +
                                str(response.status_code) + response.text)
            return response.content

        if self.method == "POST" or self.method == "post":
            response = requests.post(self.url,
                                     data=self.data,
                                     headers=self.headers,
                                     cookies=self.cookies)

            if response.status_code != 200:
                raise Exception("Errorin API response. status_code: "
                                + str(response.status_code) + response.text)
            return response.content
        return None

    # This method will respond true if the status code is 200
    def dial_without_exception(self):
        try:
            self.dial()
            return True
        except BaseException:
            return False
