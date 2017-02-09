import csv
import json

from . import utils


class _Output(object):
    def __init__(self, columns, format_func, fh):
        """Columns is a list of column names that will be picked from the
        formatted data dict. format_func is called for each row, and must
        return a dictionary. fh is an open file handle, results are written to.
        """
        self.columns = columns
        self.format_func = format_func
        self.fh = fh


class JsonOutput(_Output):
    def __call__(self, records):
        data = [self.format_func(record) for record in records]
        json.dump(data, self.fh)

        return self.fh


class CsvOutput(_Output):
    def __call__(self, records):
        writer = csv.DictWriter(self.fh, self.columns, extrasaction='ignore')

        for record in records:
            out = self.format_func(record)
            out = utils.encode_dict(out)
            writer.writerow(out)

        self.fh


_formatters = {
    'json': JsonOutput,
    'csv': CsvOutput,
}


def get_formatter(name):
    return _formatters[name]
