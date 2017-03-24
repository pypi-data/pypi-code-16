import os

import pytest

from sulfur import Client


@pytest.fixture
def client(server, port):
    return Client(base_url='http://localhost:%s/' % port)


def test_client(client):
    r = client.get('')
    assert 'base.html' in r.data


def test_client_get_page(client, server_path):
    with open(os.path.join(server_path, 'base.html'), 'r') as F:
        data = F.read()

    assert data == client.get('base.html').data
