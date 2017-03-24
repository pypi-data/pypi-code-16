import os

import pytest
import requests

from sulfur.testserver import TestServer as Server


@pytest.yield_fixture
def tmp_server():
    base = os.path.dirname(__file__)
    path = os.path.join(base, 'data')
    server = Server(port=8888, path=path)
    yield server
    if server.running: server.stop()


def test_server_can_start_and_stop(tmp_server):
    tmp_server.start()
    assert tmp_server.base_url == 'http://localhost:8888/'
    tmp_server.stop()


def test_server_can_serve_pages(tmp_server, base_source):
    tmp_server.start()
    response = requests.get(tmp_server.base_url + 'base.html')
    data = response.content.decode('utf8')
    assert 'Title' in data
    assert 'Hello world' in data
    assert base_source == data
    tmp_server.stop()


