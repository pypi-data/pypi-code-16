import pytest


@pytest.mark.asyncio
def test_files_cp(client):
    yield from client.files.cp("source", "path")
    client.transport.request.assert_called_with(
        'get', endpoint='/files/cp', params=[('arg', 'source'), ('arg', 'path')]
    )


@pytest.mark.asyncio
def test_files_flush(client):
    yield from client.files.flush("path")
    client.transport.request.assert_called_with('get', endpoint='/files/flush', params={'arg': 'path'})


@pytest.mark.asyncio
def test_files_ls(client):
    yield from client.files.ls("path", False)
    client.transport.request.assert_called_with('get', endpoint='/files/ls', params={'arg': "path", "l": False})


@pytest.mark.asyncio
def test_files_mkdir(client):
    yield from client.files.mkdir("path", False)
    client.transport.request.assert_called_with('get', endpoint='/files/mkdir',
                                                params={'arg': 'path', 'parent': False})


@pytest.mark.asyncio
def test_files_mv(client):
    yield from client.files.mv("source", "dest")
    client.transport.request.assert_called_with('get', endpoint='/files/mv',
                                                params=[('arg', 'source'), ('arg', 'dest')])


@pytest.mark.asyncio
def test_files_read(client):
    yield from client.files.read("path", 1, 10)
    client.transport.request.assert_called_with('get', endpoint='/files/read', params={
        'arg': 'path',
        'offset': 1,
        'count': 10
    })


@pytest.mark.asyncio
def test_files_rm(client):
    yield from client.files.rm('path', False)
    client.transport.request.assert_called_with('get', endpoint='/files/rm', params={
        'arg': 'path',
        'recursive': False
    })


@pytest.mark.asyncio
def test_files_stat(client):
    yield from client.files.stat('path', False, False)
    client.transport.request.assert_called_with('get', endpoint='/files/stat', params={
        'arg': 'path',
        'hash': False,
        'size': False
    })


@pytest.mark.asyncio
def test_files_write(client, dummyfilestream):
    yield from client.files.write("path", dummyfilestream, 1, False, False, 10)
    client.transport.request.assert_called_with('post', endpoint='/files/write', params={
        'arg': "path",
        'offset': 1,
        'create': False,
        'truncate': False,
        'count': 10
    }, data={
        'file': dummyfilestream
    })
    pass
