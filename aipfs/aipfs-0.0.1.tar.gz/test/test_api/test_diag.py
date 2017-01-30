import pytest


@pytest.mark.asyncio
def test_diag_cmds_clear(client):
    yield from client.diag.cmds_clear()
    client.transport.request.assert_called_with('get', endpoint='/diag/cmds/clear')


@pytest.mark.asyncio
def test_diag_cmds_set_time(client):
    yield from client.diag.cmds_set_time("time")
    client.transport.request.assert_called_with('get', endpoint='/diag/cmds/set-time', params={
        'arg': 'time'
    })


@pytest.mark.asyncio
def test_diag_net(client):
    yield from client.diag.net("text")
    client.transport.request.assert_called_with('get', endpoint='/diag/net', params={
        'vis': 'text'
    })


@pytest.mark.asyncio
def test_diag_sys(client):
    yield from client.diag.sys()
    # curl "http://localhost:5001/api/v0/diag/sys"
    client.transport.request.assert_called_with('get', endpoint='/diag/sys')
