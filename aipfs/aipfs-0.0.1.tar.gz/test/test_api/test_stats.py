import pytest


@pytest.mark.asyncio
def test_stats_bitswap(client):
    yield from client.stats.bitswap()
    client.transport.request.assert_called_with(
        'get', endpoint='/stats/bitswap'
    )


@pytest.mark.asyncio
def test_stats_bw(client):
    yield from client.stats.bw('peer', 'proto', False, '1s')
    client.transport.request.assert_called_with(
        'get', endpoint='/stats/bw',
        params=[('peer', 'peer'), ('proto', 'proto'), ('poll', False), ('interval', '1s')]
    )


@pytest.mark.asyncio
def test_stats_repo(client):
    # curl "http://localhost:5001/api/v0/stats/repo?human=false"
    yield from client.stats.repo(False)
    client.transport.request.assert_called_with(
        'get', endpoint='/stats/repo', params=[('human', False)]
    )
