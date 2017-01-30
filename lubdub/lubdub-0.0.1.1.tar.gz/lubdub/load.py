""" Code for loading data into memory, e.g. from the data/* directories. """


def load_plaintext_rrs(filepath, sep='\n'):
    """ Read data in from given filepath and return a list of integer RRs points. 

    :param filepath: (str) abosolute or relative path to file containing RRs
    :param sep: (str) separator between RR numbers [default: newline]
    :return rrs: (list) integers
    """
    return [int(item) for item in open(filepath).read().split(sep) if item]

