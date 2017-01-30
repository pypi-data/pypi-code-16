import pytest


@pytest.mark.asyncio
def test_swarm_addrs_local(client):
    yield from client.swarm.addrs.local(False)
    client.transport.request.assert_called_with(
        'get', endpoint='/swarm/addrs/local',
        params=[('id', False)]
    )


@pytest.mark.asyncio
def test_swarm_connect(client):
    yield from client.swarm.connect('address')
    client.transport.request.assert_called_with(
        'get', endpoint='/swarm/connect',
        params=[('arg', 'address')]
    )


@pytest.mark.asyncio
def test_swarm_disconnect(client):
    yield from client.swarm.disconnect('address')
    client.transport.request.assert_called_with(
        'get', endpoint='/swarm/disconnect',
        params=[('arg', 'address')]
    )


@pytest.mark.asyncio
def test_swarm_filters_add(client):
    yield from client.swarm.filters.add('address')
    client.transport.request.assert_called_with(
        'get', endpoint='/swarm/filters/add',
        params=[('arg', 'address')]
    )


@pytest.mark.asyncio
def test_swarm_filters_rm(client):
    yield from client.swarm.filters.rm('address')
    client.transport.request.assert_called_with(
        'get', endpoint='/swarm/filters/rm',
        params=[('arg', 'address')]
    )


@pytest.mark.asyncio
def test_swarm_peers(client):
    yield from client.swarm.peers(None)
    client.transport.request.assert_called_with(
        'get', endpoint='/swarm/peers',
        params=[('verbose', None)]
    )
