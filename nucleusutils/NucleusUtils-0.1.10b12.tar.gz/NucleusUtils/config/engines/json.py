import json

from .base import BaseLoader


class JsonLoader(BaseLoader):
    def parse(self, file: open) -> dict:
        return json.load(file)
