import pytest


@pytest.mark.asyncio
def test_refs_local(client):
    # curl "http://localhost:5001/api/v0/refs/local"
    yield from client.refs.local()
    client.transport.request.assert_called_with(
        'get',
        endpoint='/refs/local'
    )
