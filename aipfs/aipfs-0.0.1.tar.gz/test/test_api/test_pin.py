import pytest


@pytest.mark.asyncio
def test_pin_add(client):
    yield from client.pin.add("ipfs-path", True)
    client.transport.request.assert_called_with(
        'get', endpoint='/pin/add',
        params=[('arg', 'ipfs-path'), ('recursive', True)]
    )


@pytest.mark.asyncio
def test_pin_ls(client):
    yield from client.pin.ls('ipfs-path', 'all', False)
    client.transport.request.assert_called_with(
        'get', endpoint='/pin/ls',
        params=[('arg', 'ipfs-path'), ('type', 'all'), ('quiet', False)]
    )


@pytest.mark.asyncio
def test_pin_rm(client):
    # curl "http://localhost:5001/api/v0/pin/rm?arg=<ipfs-path>&recursive=true"
    yield from client.pin.rm('ipfs-path', True)
    client.transport.request.assert_called_with(
        'get', endpoint='/pin/rm',
        params=[('arg', 'ipfs-path'), ('recursive', True)]
    )