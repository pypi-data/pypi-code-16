import pytest

from aiohttp.test_utils import make_mocked_request

import aiohttp_cas.handlers

async def test_logout_handler():
    req = make_mocked_request('GET', '/')

async def test_login_hanlder():
    pass
