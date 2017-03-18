from . import parse_source_path

import unicodecsv as csv


class CsvReader(object):
    def __init__(self, source_path):
        self.source_path = source_path
        self.return_as_dict = False
        self.delimiter = None
        self.quoting = None
        self.escape_char = None
        args = parse_source_path(self.source_path)
        if "return_as" in args:
            self.return_as_dict = True
        if "quoting" in args:
            self.quoting = args.get("quoting")
        if "escape_char" in args:
            self.escape_char = args.get("escape_char")
        if "delimiter" in args:
            self.delimiter = args.get("delimiter")
        self.path = args.get("path")

    def read(self):
        reader = open(self.path, "rb")
        fieldnames = next(reader).split(self.delimiter if self.delimiter else ",")
        if self.return_as_dict:
            data = csv.DictReader(reader, fieldnames=fieldnames,
                                  quoting=csv.QUOTE_ALL if not self.quoting else self.quoting,
                                  escapechar=None if not self.escape_char else self.escape_char)
            for row in data:
                yield row
        else:
            data = csv.reader(reader)
            for row in data:
                yield row

        reader.close()


