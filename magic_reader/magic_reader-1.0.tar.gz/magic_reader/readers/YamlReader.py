import yaml


class YamlReader(object):
    def __init__(self, source_path):
        self.source_path = source_path

    def read(self):
        with open(self.source_path, "rb") as reader:
            data = yaml.load(reader)
        yield data
