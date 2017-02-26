import traceback
import sys


class ElementalError(Exception):
    """
    Base class for Elemental exceptions.
    """

    @property
    def message(self):
        """
        str: Human readable string describing the exception.
        """
        return self._message

    @property
    def inner_error(self):
        """
        Exception: Exception instance that caused this exception.
        """
        return self._inner_error

    @property
    def traceback(self):
        """
        str: Frame where inner_error was raised.
        """
        if self._inner_error:
            return self._traceback
        return None

    def __init__(self, message, inner_error=None):
        """
        Initializes a new `ElementalError` instance.

        Args:
            message (str): Human readable string describing the exception.
            inner_error (Optional[Exception]): Exception instance that caused
                this exception.
        """
        self._message = message
        self._inner_error = inner_error
        self._traceback = traceback.format_tb(sys.exc_info()[-1])

    def __str__(self):
        if self._inner_error:
            return '{0}\n{1}'.format(self._message, self.traceback)
        return self._message
