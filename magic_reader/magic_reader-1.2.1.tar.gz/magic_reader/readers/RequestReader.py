import requests
from fake_useragent import UserAgent
from retrying import retry

from . import parse_source_path


class RequestReader(object):

    def __init__(self, source_path, real_path=None):
        self.source_path = source_path
        self.ua = UserAgent(cache=True)
        args = parse_source_path(self.source_path)
        self.retry_count = int(args.get("retry_count"))
        self.wait_between = int(args.get("wait_between").replace("s", "")) * 60  # to milliseconds.
        self.method = args.get("method")
        self.url = args.get("url")
        self.return_as = args.get("return_as")

    def read(self):

        @retry(stop_max_attempt_number=self.retry_count, wait_fixed=self.wait_between)
        def fetch():
            request = getattr(requests, self.method)(self.url, headers={'User-Agent': self.ua.google})
            if request.status_code == 200:
                if self.return_as in ("text", "txt"):
                    yield request.text
                elif self.return_as in "json":
                    yield request.json()

        return fetch()

