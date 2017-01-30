import pytest


@pytest.mark.asyncio
def test_repo_fsck(client):
    yield from client.repo.fsck()
    client.transport.request.assert_called_with(
        'get',
        endpoint='/repo/fsck'
    )


@pytest.mark.asyncio
def test_repo_gc(client):
    yield from client.repo.gc(False)
    client.transport.request.assert_called_with(
        'get',
        endpoint='/repo/gc',
        params=[('quiet', False)]
    )


@pytest.mark.asyncio
def test_repo_stat(client):
    yield from client.repo.stat(False)
    client.transport.request.assert_called_with(
        'get', endpoint='/repo/stat',
        params=[('human', False)]
    )


@pytest.mark.asyncio
def test_repo_verify(client):
    yield from client.repo.verify()
    client.transport.request.assert_called_with(
        'get', endpoint='/repo/verify'
    )


@pytest.mark.asyncio
def test_repo_version(client):
    # curl "http://localhost:5001/api/v0/repo/version?quiet=<value>"
    yield from client.repo.version(True)
    client.transport.request.assert_called_with(
        'get', endpoint='/repo/version',
        params=[('quiet', True)]
    )
