import pytest


@pytest.mark.asyncio
def test_config_edit(client):
    yield from client.config.edit()
    client.transport.request.assert_called_with('get', endpoint='/config/edit')


@pytest.mark.asyncio
def test_config_replace(client, dummyfilestream):
    yield from client.config.replace(dummyfilestream)
    client.transport.request.assert_called_with('post', endpoint='/config/replace', data={
        'file': dummyfilestream
    })


@pytest.mark.asyncio
def test_config_show(client):
    yield from client.config.show()
    client.transport.request.assert_called_with('get', endpoint='/config/show')
