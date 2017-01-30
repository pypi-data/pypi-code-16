import pytest


@pytest.mark.asyncio
def test_object_data(client):
    yield from client.object.data('hash')
    client.transport.request.assert_called_with('get', endpoint='/object/data', params={'arg': 'hash'})


@pytest.mark.asyncio
def test_object_diff(client):
    yield from client.object.diff("object1", "object2", False)
    client.transport.request.assert_called_with('get', endpoint='/object/diff', params=[
        ('arg', 'object1'), ('arg', 'object2'), ('verbose', False)
    ])


@pytest.mark.asyncio
def test_object_get(client):
    yield from client.object.get('key')
    client.transport.request.assert_called_with('get', endpoint='/object/get', params={'arg': 'key'})


@pytest.mark.asyncio
def test_object_links(client):
    yield from client.object.links('key', False)
    client.transport.request.assert_called_with('get', endpoint='/object/links',
                                                params={'arg': 'key', 'headers': False})


@pytest.mark.asyncio
def test_object_new(client):
    yield from client.object.new('template')
    client.transport.request.assert_called_with('get', endpoint='/object/new', params={'arg': 'template'})


@pytest.mark.asyncio
def test_object_put(client, dummyfilestream):
    yield from client.object.put(dummyfilestream, inputenc='json', datafieldenc='text')
    client.transport.request.assert_called_with(
        'get', endpoint='/object/put',
        data={
            'file': dummyfilestream
        }, params={
            'inputenc': 'json', 'datafieldenc': 'text'
        })


@pytest.mark.asyncio
def test_object_patch_add_link(client):
    yield from client.object.patch.add_link("hash", "namelink", "ipfsobject", False)
    client.transport.request.assert_called_with(
        'get', endpoint='/object/patch/add-link', params=[
            ("arg", "hash"),
            ("arg", "namelink"),
            ("arg", "ipfsobject"),
            ("create", False)
        ]
    )


@pytest.mark.asyncio
def test_object_patch_append_data(client, dummyfilestream):
    yield from client.object.patch.append_data(dummyfilestream, "node")
    client.transport.request.assert_called_with(
        'post', endpoint='/object/patch/append-data', params=[
            ("arg",  "node")
        ], data={
            "file": dummyfilestream
        }
    )


@pytest.mark.asyncio
def test_object_patch_rm_link(client):
    yield from client.object.patch.rm_link("hashname", "name")
    client.transport.request.assert_called_with(
        'get', endpoint='/object/patch/rm-link', params=[
            ('arg', "hashname"),
            ('arg', "name")
        ]
    )


@pytest.mark.asyncio
def test_object_patch_set_data(client, dummyfilestream):
    yield from client.object.patch.set_data(dummyfilestream, "hashnode")
    client.transport.request.assert_called_with(
        'get', endpoint='/object/patch/set-data',
        params=[('arg', 'hashnode')], data={"file": dummyfilestream}
    )


@pytest.mark.asyncio
def test_object_stat(client):
    # curl "http://localhost:5001/api/v0/object/stat?arg=<key>"
    yield from client.object.stat("key")
    client.transport.request.assert_called_with(
        'get', endpoint='/object/stat', params=[('arg', "key")]
    )
