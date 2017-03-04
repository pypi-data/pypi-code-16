import sys
from . import Logger


class TransportException(Exception):
    """Class to record and optionally exit script execution.

    Extends Exception. Uses `Logger` class to write errors to disk.

    Attributes
    ----------
        message: str
            Message to be logged.
        exit: bool
            Determines if the `TransportException` should also
            exit script execution (for fatal errors only).

    """

    def __init__(self, message, exit=False):
        super(TransportException, self).__init__(message)
        Logger.log(message)
        if exit:
            sys.exit(1)
