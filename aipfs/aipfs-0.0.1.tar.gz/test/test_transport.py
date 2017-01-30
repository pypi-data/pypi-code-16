import pytest
from aipfs.transport import AsyncHTTP


@pytest.mark.asyncio
def test_async_http():
    with AsyncHTTP(base_url="https://python.org") as transport:
        res = yield from transport.request("get", "/")
        assert res.status == 200
