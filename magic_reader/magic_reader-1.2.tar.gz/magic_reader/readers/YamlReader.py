from . import parse_source_path, s3_read
import yaml
import cStringIO


class YamlReader(object):
    def __init__(self, source_path, real_path=None):
        self.source_path = source_path
        self.real_path = real_path
        if real_path:
            args = parse_source_path(self.real_path)
        else:
            args = parse_source_path(self.source_path)
        self.path = args.get("path")
        self.chunk_size = None if "chunk_size" not in args else args["chunk_size"]

    def read(self):
        if "s3" in self.path:
            elements = ""
            for element in s3_read(path=self.path, chunk_size=self.chunk_size):
                elements += element
            data = yaml.load(cStringIO.StringIO(elements))
            return data
        try:
            with open(self.path, "rb") as reader:
                data = yaml.load(reader)
        except IOError as err:
            raise err
        return data
