from . import parse_source_path


class TextReader(object):
    def __init__(self, source_path):
        self.source_path = source_path
        args = parse_source_path(self.source_path)
        self.path = args.get("path")

    def read(self):
        reader = open(self.path, "rb")
        for row in reader:
            yield row

        reader.close()
