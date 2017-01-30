import pytest


@pytest.mark.asyncio
def test_name_publish(client):
    yield from client.name.publish('ipfs-path', True, "300s", "ttl")
    client.transport.request.assert_called_with(
        'get', endpoint='/name/publish',
        params=[
            ('arg', 'ipfs-path'),
            ('resolve', True),
            ('lifetime', '300s'),
            ('ttl', 'ttl')
        ]
    )


@pytest.mark.asyncio
def test_name_resolve(client):
    # curl "http://localhost:5001/api/v0/name/resolve?arg=<name>&recursive=false&nocache=false"
    yield from client.name.resolve('ipns-name', False, False)
    client.transport.request.assert_called_with(
        'get', endpoint='/name/resolve',
        params=[
            ('arg', 'ipns-name'),
            ('recursive', False),
            ('nocache', False)
        ]
    )
