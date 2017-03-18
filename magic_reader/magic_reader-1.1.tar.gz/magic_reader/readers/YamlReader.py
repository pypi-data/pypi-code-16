from . import parse_source_path
import yaml


class YamlReader(object):
    def __init__(self, source_path):
        self.source_path = source_path
        args = parse_source_path(self.source_path)
        self.path = args.get("path")

    def read(self):
        try:
            with open(self.path, "rb") as reader:
                data = yaml.load(reader)
        except IOError as err:
            raise err
        return data
