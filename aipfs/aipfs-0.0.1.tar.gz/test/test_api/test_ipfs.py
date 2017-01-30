import pytest


@pytest.mark.asyncio
def test_resolve(client):
    yield from client.resolve("name", recursive=False)
    client.transport.request.assert_called_with('get', endpoint='/resolve', params={
        'arg': 'name',
        'recursive': False
    })


@pytest.mark.asyncio
def test_ping(client):
    yield from client.ping("123", count=10)
    client.transport.request.assert_called_with('get', endpoint='/ping', params={
        'arg': '123',
        'count': 10
    })


@pytest.mark.asyncio
def test_mount(client):
    yield from client.mount("ipfs-path", "ipns-path")
    client.transport.request.assert_called_with('get', endpoint='/mount', params={
        'ipfs-path': 'ipfs-path',
        'ipns-path': 'ipns-path'
    })


@pytest.mark.asyncio
def test_ls(client):
    yield from client.ls("ipfs-path", headers=False, resolve_type=True)
    client.transport.request.assert_called_with('get', endpoint="/ls", params={
        "arg": "ipfs-path",
        "headers": False,
        "resolve-type": True
    })


@pytest.mark.asyncio
def test_id(client):
    yield from client.id(peer_id="123", _format="")
    client.transport.request.assert_called_with('get', endpoint="/id", params={
        "arg": "123",
        "format": ""
    })


@pytest.mark.asyncio
def test_get(client):
    yield from client.get("ipfs-path", output="", archive=False, compress=False, compression_level=-1)
    client.transport.request.assert_called_with('get', endpoint="/get", params={
        "arg": "ipfs-path",
        "output": "",
        "archive": False,
        "compress": False,
        "compression-level": -1
    })


@pytest.mark.asyncio
def test_dns(client):
    yield from client.dns("domain-name", recursive=False)
    client.transport.request.assert_called_with(
        "get", endpoint="/dns",
        params={
            "arg": "domain-name",
            "recursive": False
        }
    )


@pytest.mark.asyncio
def test_cat(client):
    yield from client.cat("ipfs-path")
    client.transport.request.assert_called_with(
        "get", endpoint="/cat",
        params={
            "arg": "ipfs-path"
        }
    )


@pytest.mark.asyncio
def test_add(client, dummyfilestream):
    yield from client.add(
        filestream=dummyfilestream,
        recursive=False,
        quiet=False,
        silent=False,
        progress=False,
        trickle=False,
        only_hash=False,
        wrap_with_directory=False,
        hidden=False,
        chunker="",
        pin=True
    )
    client.transport.request.assert_called_with(
        "post", endpoint="/add",
        data={'file': dummyfilestream},
        params={
            "recursive": False,
            "quiet": False,
            "silent": False,
            "progress": False,
            "trickle": False,
            "only_hash": False,
            "wrap_with_directory": False,
            "hidden": False,
            "chunker": "",
            "pin": True
        }
    )


@pytest.mark.asyncio
def test_version(client):
    yield from client.version()
    client.transport.request.assert_called_with("get", endpoint="/version")
