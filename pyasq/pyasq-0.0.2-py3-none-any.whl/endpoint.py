from typing import Callable

import requests

from .conversion import Wrapper


class Endpoint:

    def __init__(self, path: str, return_type: Callable):
        self.path = path
        self.base_url = None
        self.return_type = return_type

    @property
    def url(self) -> str:
        return self.base_url + self.path

    def get(self) -> Wrapper:
        return self.return_type(requests.get(self.url).json())
