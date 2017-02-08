""" Code for loading data into memory, e.g. from the data/* directories. """


def load_plaintext_rrs(filepath, sep='\n'):
    """ Read data in from given filepath and return a list of integer RRs points. 

    :param filepath: (str) abosolute or relative path to file containing RRs
    :param sep: (str) separator between RR numbers [default: newline]
    :return rrs: (list) integers
    """
    return [int(item) for item in open(filepath).read().split(sep) if item]

def load_csv_rrs(filepath, sep=','):
    """ Read data in from given filepath and return a list of integer RRs points. 

    :param filepath: (str) abosolute or relative path to file containing RRs
    :param sep: (str) separator between RR numbers [default: newline]
    :return rrs: (list) integers
    """
    values = []
    for item in open(filepath).read().split('\n'):
        try:
            values.append(float(item.split(sep)[0]))
        except (ValueError, TypeError, IndexError):
            pass
    return values


def load_EliteHRV_rrs(filepath):
    return load_plaintext_rrs(filepath)

def load_HRV4Training_rrs(filepath):
    return load_csv_rrs(filepath, ',')


