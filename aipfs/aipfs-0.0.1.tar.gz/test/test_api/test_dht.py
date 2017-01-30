import pytest


@pytest.mark.asyncio
def test_dht_findpeer(client):
    yield from client.dht.findpeer('peer_id', verbose=False)
    client.transport.request.assert_called_with('get', endpoint='/dht/findpeer', params={
        'arg': 'peer_id',
        'verbose': False
    })


@pytest.mark.asyncio
def test_dht_findprovs(client):
    yield from client.dht.findprovs('key', verbose=False)
    client.transport.request.assert_called_with('get', endpoint='/dht/findprovs', params={
        'arg': 'key',
        'verbose': False
    })


@pytest.mark.asyncio
def test_dht_get(client):
    yield from client.dht.get('key', verbose=False)
    client.transport.request.assert_called_with('get', endpoint='/dht/get', params={
        'arg': 'key',
        'verbose': False
    })


@pytest.mark.asyncio
def test_dht_put(client):
    yield from client.dht.put('key', 'value', verbose=False)
    client.transport.request.assert_called_with('get', endpoint='/dht/put', params=[
        ('arg', 'key'), ('arg', 'value'), ('verbose', False)
    ])


@pytest.mark.asyncio
def test_dht_query(client):
    yield from client.dht.query("peer_id")
    client.transport.request.assert_called_with('get', endpoint='/dht/query', params={
        'arg': 'peer_id',
        'verbose': False
    })
