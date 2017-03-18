from . import parse_source_path
import ujson


class JsonReader(object):
    def __init__(self, source_path):
        self.source_path = source_path
        args = parse_source_path(self.source_path)
        self.path = args.get("path")

    def read(self):
        with open(self.path, "rb") as reader:
            data = ujson.load(reader)
        return data


