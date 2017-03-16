import collections
import io
import sys
from contextlib import contextmanager


class Capture(collections.UserString):
    """
    Captures output after leaving block.

    Outputs are written as strings in the output and error attributes.
    """
    stdout = None
    stderr = None
    original_stdout = None
    original_stderr = None
    out = ''
    error = ''

    @property
    def data(self):
        return self.out

    def __init__(self):
        pass

    def __str__(self):
        return self.out or ''


@contextmanager
def capture_output(join_err=False):
    """
    Captures all output inside the block.

    Saves results in the `out`, and `error` attributes of the context manager object.

    Example:

        >>> with capture_output() as data:
        ...     print('foo')
        ...     print('bar')
        >>> data.out
        'foo\nbar\n'
    """

    # Prepare with block
    capture = Capture()
    capture.original_stdout = sys.stdout
    capture.original_stderr = sys.stdout
    capture.stdout = sys.stdout = io.StringIO()
    capture.stderr = sys.stderr
    if join_err:
        capture.stderr = sys.stderr = sys.stdout
    else:
        capture.stderr = sys.stderr = io.StringIO()

    # Enter with block
    try:
        yield capture

    # Leave with block
    finally:
        capture.out = capture.stdout.getvalue() or ''
        sys.stdout = capture.original_stdout
        if not join_err:
            capture.error = capture.stderr.getvalue() or ''
        sys.stderr = capture.original_stderr
