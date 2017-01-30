import pytest


@pytest.mark.asyncio
def test_block_get(client):
    yield from client.block.get("hash")
    client.transport.request.assert_called_with("get", endpoint="/block/get", params={
        "arg": "hash"
    })


@pytest.mark.asyncio
def test_block_put(client, dummyfilestream):
    yield from client.block.put(dummyfilestream)
    client.transport.request.assert_called_with("post", endpoint="/block/put", data={
        'file': dummyfilestream
    })


@pytest.mark.asyncio
def test_block_stat(client):
    yield from client.block.stat("hash")
    client.transport.request.assert_called_with('get', endpoint="/block/stat", params={
        'arg': "hash"
    })