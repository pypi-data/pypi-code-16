import requests
from fake_useragent import UserAgent
from retrying import retry

from . import parse_source_path


class RequestReader(object):

    def __init__(self, source_path):
        self.source_path = source_path
        self.parsed_arguments = None
        self.ua = UserAgent(cache=True)

    def read(self):
        self.parsed_arguments = parse_source_path(self.source_path)

        @retry(stop_max_attempt_number=int(self.parsed_arguments["retry_count"]),
               wait_fixed=int(self.parsed_arguments["wait_between"].replace("s", "")))
        def fetch():
            request = getattr(requests, self.parsed_arguments["method"])(self.parsed_arguments["url"],
                                                                         headers={'User-Agent': self.ua.google})
            print request
            if request.status_code == 200:
                if self.parsed_arguments["return_as"] in ("text", "txt"):
                    yield request.text
                elif self.parsed_arguments["return_as"] in "json":
                    yield request.json()

        return fetch()

