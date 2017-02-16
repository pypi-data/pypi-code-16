import datetime
import pytest

import fedfind.const
import fedfind.helpers

# config decorators
net = pytest.mark.net

class TestHelpers:
    """Tests for the functions in helpers.py."""
    def test_date_check(self):
        invalid = 'notadate'
        # this looks a bit silly, but we want the values of 'valid'
        # and 'obj' to match
        now = datetime.datetime.now()
        valid = now.strftime('%Y%m%d')
        obj = datetime.datetime.strptime(valid, '%Y%m%d')

        # Default case: checking valid obj or str should return obj
        assert fedfind.helpers.date_check(obj, out='obj') == obj
        assert fedfind.helpers.date_check(valid, out='obj') == obj
        assert fedfind.helpers.date_check(obj) == obj
        assert fedfind.helpers.date_check(valid) == obj

        # Checking valid obj or str with out='str' should return str
        assert fedfind.helpers.date_check(obj, out='str') == valid
        assert fedfind.helpers.date_check(valid, out='str') == valid

        # Checking valid with out='both' should return a tuple of both
        assert fedfind.helpers.date_check(obj, out='both') == (valid, obj)
        assert fedfind.helpers.date_check(valid, out='both') == (valid, obj)

        # Checking invalid with fail_raise=False should return False
        assert fedfind.helpers.date_check(invalid, fail_raise=False) is False

        # Checking invalid with fail_raise=True or default should
        # raise ValueError
        with pytest.raises(ValueError):
            fedfind.helpers.date_check(invalid, fail_raise=True)
        with pytest.raises(ValueError):
            fedfind.helpers.date_check(invalid)

    @net
    def test_url_exists(self):
        httpgood = fedfind.const.HTTPS_DL
        httpbad = httpgood + 'foobarmonkeyswhat'
        rsyncgood = fedfind.const.RSYNC
        rsyncbad = rsyncgood + '/foobarmonkeyswhat'
        invalid = 'jfohpjsph#^3#@^#'

        assert fedfind.helpers.url_exists(httpgood) is True
        assert fedfind.helpers.url_exists(httpbad) is False
        assert fedfind.helpers.url_exists(rsyncgood) is True
        assert fedfind.helpers.url_exists(rsyncbad) is False

        with pytest.raises(ValueError):
            fedfind.helpers.url_exists(invalid)

    def test_comma_list(self):
        # it splits lists on commas. it ain't rocket science.
        assert fedfind.helpers.comma_list('foo,bar,moo') == ['foo', 'bar', 'moo']
