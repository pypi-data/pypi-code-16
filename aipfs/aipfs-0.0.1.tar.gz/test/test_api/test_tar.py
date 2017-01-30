import pytest


@pytest.mark.asyncio
def test_tar_add(client, dummyfilestream):
    yield from client.tar.add(dummyfilestream)
    client.transport.request.assert_called_with(
        'post', endpoint='/tar/add', data={'file': dummyfilestream}
    )


@pytest.mark.asyncio
def test_tar_cat(client):
    yield from client.tar.cat('ipfs-path')
    client.transport.request.assert_called_with(
        'get', endpoint='/tar/cat', params=[('arg', 'ipfs-path')]
    )

