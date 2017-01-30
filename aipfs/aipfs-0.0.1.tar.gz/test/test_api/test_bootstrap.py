import pytest


@pytest.mark.asyncio
def test_bootstrap_add_default(client):
    yield from client.bootstrap.add_default()
    client.transport.request.assert_called_with('get', endpoint='/bootstrap/add/default')


@pytest.mark.asyncio
def test_bootstrap_list(client):
    yield from client.bootstrap.list()
    client.transport.request.assert_called_with('get', endpoint='/bootstrap/list')


@pytest.mark.asyncio
def test_bootstrap_rm_all(client):
    yield from client.bootstrap.rm_all()
    client.transport.request.assert_called_with('get', endpoint='/bootstrap/rm/all')
