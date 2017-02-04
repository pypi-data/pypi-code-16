from __future__ import absolute_import
import hashlib

import pytest
from w3lib.util import to_bytes

from cacheutils.utils import parse_url
from cacheutils.utils import get_crc32, to_signed32
from cacheutils.utils import hostname_local_fingerprint, sha1


# parse_url
def test_parse_url__simple_url():
    simple_url = 'http://www.example.com'
    parse_url(simple_url) == ('http', 'www.example.com', '', '', '', '')


def test_parse_url__complete_url():
    complete_url = 'http://username:password@www.example.com:80'\
        '/some/page/do?a=1&b=2&c=3#frag'
    parse_url(complete_url) == \
        ('http', 'username:password@www.example.com:80', '/some/page/do', '',
         'a=1&b=2&c=3', 'frag')


def test_parse_url__already_parsed():
    simple_url = 'http://www.example.com'
    result = parse_url(simple_url)
    parse_url(result) == result


# get_crc32
def test_get_crc32__bytes():
    assert get_crc32(b'example') == 1861000095


def test_get_crc32__ascii_unicode():
    assert get_crc32(u'example') == 1861000095


def test_get_crc32__non_ascii_unicode():
    assert get_crc32(u'example\u5000') == 1259721235


def test_get_crc32__non_ascii_bytes():
    assert get_crc32(u'example\u5000'.encode('utf8')) == 1259721235


def test_get_crc32__negative_crc32():
    assert get_crc32(b'1') == -2082672713


def test_get_crc32__crc32_range():
    left, right = -2**31, 2**31 - 1
    for x in range(10000):
        bytestr = hashlib.md5(str(x).encode('ascii')).hexdigest()
        assert left <= get_crc32(bytestr) <= right
    for x in [left, left + 1, right - 1, right, right + 1,
              2**32 - 2, 2**32 - 1]:
        assert left <= to_signed32(x) <= right


# DATA
URLS = (
    u"https://news.yandex.ru/yandsearch?cl4url=top.rbc.ru/politics"
    "/14/07/2015/55a50b509a79473f583e104c&lang=ru&lr=54#fragment",
    u"TestString",
    u"http://www.example.com/some/page\u5000/"
)


# sha1
@pytest.mark.parametrize('test_input, expected',
                         zip(URLS, (
                             b'880c5e7919cb09e182bd639d724bce6d90db71eb',
                             b'd598b03bee8866ae03b54cb6912efdfef107fd6d',
                             b'28bf812b6421a46ee5bcf40c05a82e8f051ab88e'
                         )))
def test_sha1__bytes(test_input, expected):
    assert sha1(to_bytes(test_input)) == expected


@pytest.mark.parametrize('test_input, expected',
                         zip(URLS, (
                             b'880c5e7919cb09e182bd639d724bce6d90db71eb',
                             b'd598b03bee8866ae03b54cb6912efdfef107fd6d',
                             b'28bf812b6421a46ee5bcf40c05a82e8f051ab88e'
                         )))
def test_sha1__unicode(test_input, expected):
    assert sha1(test_input) == expected


# hostname_local_fingerprint
@pytest.mark.parametrize('test_input', (None, -1, 1, [], {}))
def test_hostname_local_fingerprint__not_string(test_input):
    with pytest.raises(TypeError):
        hostname_local_fingerprint(test_input)


@pytest.mark.parametrize('test_input, expected',
                         zip(URLS, (
                             b'1be68ff556fd0bbe5802d1a100850da29f7f15b1',
                             b'd598b03bee8866ae03b54cb6912efdfef107fd6d',
                             b'2ed642bbdf514b8520ab28f5da589ab28eda10a6'
                         )))
def test_hostname_local_fingerprint__bytes(test_input, expected):
    assert hostname_local_fingerprint(to_bytes(test_input)) == expected


@pytest.mark.parametrize('test_input, expected',
                         zip(URLS, (
                             b'1be68ff556fd0bbe5802d1a100850da29f7f15b1',
                             b'd598b03bee8866ae03b54cb6912efdfef107fd6d',
                             b'2ed642bbdf514b8520ab28f5da589ab28eda10a6'
                         )))
def test_hostname_local_frongerprint__unicode(test_input, expected):
    assert hostname_local_fingerprint(test_input) == expected
