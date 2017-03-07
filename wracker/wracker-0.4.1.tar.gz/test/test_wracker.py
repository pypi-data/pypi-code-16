import unittest

import testfixtures

import wracker.__main__


class WrackerResult(object):
    """Capture the result of running wracker."""
    def __init__(self, exit_code, stdout, stderr):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def main(*args):
    """Run wracker, return an object with return code and streams.

    Ensures the return code is 0.
    """
    exit_code = 0
    try:
        with testfixtures.OutputCapture(separate=True) as output:
            result = wracker.__main__.main(args)
            assert result is None, "Unexpected return value from main()"
    except SystemExit as exc:
        exit_code = exc.code

    def trim(stringio):
        return stringio.getvalue().strip()
    assert exit_code == 0, "Exit code was %s, expected 0" % exit_code
    return WrackerResult(exit_code, trim(output.stdout), trim(output.stderr))


class WrackerTest(unittest.TestCase):
    """Tests for the wracker program."""

    def test_has_version_flag(self):
        """There's a --version flag."""
        version = wracker.__version__
        version_str = 'wracker %s' % version

        result = main('--version')
        assert result.stderr == version_str
        assert result.stdout == ''
