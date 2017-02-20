from __future__ import absolute_import

import warnings
import six

from turbodbc_intern import connect as intern_connect
from turbodbc_intern import Rows

from .exceptions import translate_exceptions
from .connection import Connection

def _make_connection_string(dsn, **kwargs):
    if dsn:
        kwargs['dsn'] = dsn
    return ';'.join(["{}={}".format(key, value) for key, value in six.iteritems(kwargs)])


@translate_exceptions
def connect(dsn=None, read_buffer_size=None, rows_to_buffer=None, parameter_sets_to_buffer=None, use_async_io=False, **kwargs):
    """
    Create a connection with the database identified by the dsn
    :param dsn: data source name as given in the odbc.ini file
    :param rows_to_buffer: Number of rows which shall be buffered
                           when result sets are fetched from the server.
                           None means that the default value is used.
    :param parameter_sets_to_buffer: Number of parameter sets (rows) which
                           shall be buffered when bulk queries are sent
                           to the server.
                           None means that the default value is used.
    :param use_async_io: Set this value to true if you want to use
                         asynchronous I/O. Asynchronous I/O means that
                         while the main thread converts a batch of
                         results to Python objects, another thread
                         fetches additional results in the background.
    :param \**kwargs: You may specify additional options as you please.
                      These options will go into the connection string.
                      Valid options depend on the specific database you
                      would like to connect with (e.g. `user` or `password`)
    """    
    connection = Connection(intern_connect(_make_connection_string(dsn, **kwargs)))

    if rows_to_buffer:
        warnings.warn("Calling turbodbc.connect() with parameter rows_to_buffer is deprecated. "
                      "Instead, set the parameter read_buffer_size to turbodbc.Megabytes(x) or "
                      "turbodbc.Rows(y) instead.", DeprecationWarning)
        connection.impl.set_buffer_size(Rows(rows_to_buffer))

    if read_buffer_size:
        connection.impl.set_buffer_size(read_buffer_size)

    if parameter_sets_to_buffer:
        connection.impl.parameter_sets_to_buffer = parameter_sets_to_buffer

    connection.impl.use_async_io = use_async_io

    return connection