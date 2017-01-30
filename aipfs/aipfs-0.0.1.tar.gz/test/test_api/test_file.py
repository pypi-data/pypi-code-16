import pytest


@pytest.mark.asyncio
def test_file_ls(client):
    yield from client.file.ls("path")
    client.transport.request.assert_called_with('get', endpoint='/file/ls', params={"arg": "path"})
