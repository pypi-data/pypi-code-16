import pytest


@pytest.mark.asyncio
def test_log_level(client):
    yield from client.log.level("subsystem", "debug")
    client.transport.request.assert_called_with(
        'get', endpoint='/log/level', params=[('arg', 'subsystem'), ('arg', 'debug')]
    )


@pytest.mark.asyncio
def test_log_ls(client):
    yield from client.log.ls()
    client.transport.request.assert_called_with(
        'get', endpoint='/log/ls'
    )


@pytest.mark.asyncio
def test_log_tail(client):
    yield from client.log.tail()
    client.transport.request.assert_called_with(
        'get', endpoint='/log/tail'
    )
