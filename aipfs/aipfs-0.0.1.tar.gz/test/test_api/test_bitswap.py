import pytest


@pytest.mark.asyncio
def test_bitswap_wantlist(client):
    yield from client.bitswap.wantlist(peer="peer")
    client.transport.request.assert_called_with('get', endpoint='/bitswap/wantlist', params={
        "peer": "peer"
    })


@pytest.mark.asyncio
def test_bitswap_stat(client):
    yield from client.bitswap.stat()
    client.transport.request.assert_called_with('get', endpoint='/bitswap/stat')


@pytest.mark.asyncio
def test_bitswap_unwant(client):
    yield from client.bitswap.unwant("key")
    client.transport.request.assert_called_with('get', endpoint='/bitswap/unwant', params={
        "arg": "key"
    })
