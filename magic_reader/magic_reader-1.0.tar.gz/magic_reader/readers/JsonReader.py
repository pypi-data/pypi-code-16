import ujson


class JsonReader(object):
    def __init__(self, source_path):
        self.source_path = source_path

    def read(self):
        with open(self.source_path, "rb") as reader:
            data = ujson.load(reader)
        yield data


