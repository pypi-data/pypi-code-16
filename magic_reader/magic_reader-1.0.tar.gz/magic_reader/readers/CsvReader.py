import unicodecsv as csv


class CsvReader(object):
    def __init__(self, source_path):
        self.source_path = source_path

    def read(self):
        reader = open(self.source_path, "rb")
        data = csv.reader(reader)
        for r in data:
            yield r

        reader.close()


