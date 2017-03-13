from csv import Dialect, QUOTE_NONE, register_dialect, reader as csv_reader


class tsv_dialect(Dialect):
    delimiter = '\t'
    quotechar = ''
    doublequote = False
    skipinitialspace = False
    lineterminator = '\n'
    quoting = QUOTE_NONE

register_dialect('tsv', tsv_dialect)


def tsv_reader(text):
    return csv_reader(filter(None, text.split('\n')), dialect='tsv')
