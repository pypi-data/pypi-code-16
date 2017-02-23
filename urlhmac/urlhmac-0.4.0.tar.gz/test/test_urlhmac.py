import pytest

import testcases
import urlhmac as py

from . import php


def iterate_testcases():
    for url in testcases.URLS:
        for key in testcases.KEYS:
            for expire in testcases.EXPIRES:
                for t in testcases.TIMES:
                    yield url, key, expire, t


@pytest.mark.parametrize('implementation', [py, php])
def test_check(implementation):
    print 'Check implementation', implementation
    for url, key, expire, t in iterate_testcases():
        signed = implementation.get_secure_link(url, key, expire, t)
        assert implementation.check_secure_link(signed, key, t=t)

        # check if signed url is consistent with python implementation
        # if all implementaitons are consistent with the python version
        # all versions are consistent with each other
        assert signed == py.get_secure_link(url, key, expire, t)

        # link is expired
        assert not implementation.check_secure_link(signed, key, t + expire + 1)

        # wrong key
        assert not implementation.check_secure_link(signed, 'correct key', t=t)

        # link is manipulated
        for i in xrange(len(signed)):
            tempered = signed[:i]
            tempered += chr(ord(signed[i]) + 1)  # change charackter at pos i
            tempered += signed[i+1:]
            assert not implementation.check_secure_link(tempered, key, t=t)


def test_url_compatibity():
    # check compatibility with different base64 encodings
    for url, key, expire, t in iterate_testcases():
        signed = py.get_secure_link(url, key, expire, t)
        url = signed.replace('-', ' ')
        url = signed.replace('_', '/')
        assert py.check_secure_link(url, key, t=t)

        url = signed.replace(' ', '+')
        assert py.check_secure_link(url, key, t=t)
