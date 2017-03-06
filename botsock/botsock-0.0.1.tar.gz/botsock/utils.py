import logging
import logging.config

import yaml

from .settings import CHUNK_SIZE


def send_by_chunks(connection, data):
    first, rest = data[:CHUNK_SIZE], data[CHUNK_SIZE:]
    connection.send(first)
    if rest:
        send_by_chunks(connection, rest)


def recv_by_chunks(connection):
    data_chunk = connection.recv(CHUNK_SIZE)
    if len(data_chunk) == CHUNK_SIZE:
        return data_chunk + recv_by_chunks(connection)
    return data_chunk


def get_logger(name, logfile):
    with open(logfile) as config:
        logging.config.dictConfig(yaml.load(config))
    logger = logging.getLogger(name)
    return logger


def get_data_info(data):
    msg = "(type - %s, length - %s)"
    data_type = data.__class__.__name__
    data_length = len(data)
    return msg % (data_type, data_length)
