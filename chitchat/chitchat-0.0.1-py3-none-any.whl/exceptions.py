"""
chitchat.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains chitchat's custom exceptions.
"""
class ChitchatException(Exception):
    """Base exception that all custom exceptions inherit from."""


class ConnectionNotOpen(ChitchatException, ValueError):
    """Attempted to read from or write to a closed connection."""

    def __init__(self, message=None):
        if not message:
            message = 'I/O operation on closed connection.'

        super().__init__(message)
