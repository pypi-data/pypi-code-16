from . import parse_source_path, s3_read

import unicodecsv as csv
import cStringIO


class CsvReader(object):
    def __init__(self, source_path, real_path=None):
        self.source_path = source_path
        self.return_as_dict = False
        self.delimiter = None
        self.quoting = None
        self.escape_char = None
        self.real_path = real_path
        if real_path:
            args = parse_source_path(self.real_path)
        else:
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
        self.chunk_size = None if "chunk_size" not in args else args["chunk_size"]

    def read(self):
        if "s3" in self.path:
            print self.real_path
            elements = ""
            for element in s3_read(path=self.path, chunk_size=self.chunk_size):
                elements += element
            if self.return_as_dict:
                fieldnames = next(cStringIO.StringIO(elements)).split(self.delimiter if self.delimiter else ",")
                data = csv.DictReader(cStringIO.StringIO(elements), fieldnames=fieldnames,
                                      quoting=csv.QUOTE_ALL if not self.quoting else self.quoting,
                                      escapechar=None if not self.escape_char else self.escape_char)
                for row in data:
                    yield row
            else:
                data = csv.reader(cStringIO.StringIO(elements), delimiter=self.delimiter if self.delimiter else ",",
                                  quoting=csv.QUOTE_ALL, escapechar=None if not self.escape_char else self.escape_char)
                for row in data:
                    yield row
        else:
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


